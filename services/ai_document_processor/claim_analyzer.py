"""
Claim Analyzer
Matches claims against policy terms and calculates reimbursements
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from groq import Groq
import openai
import google.generativeai as genai

from services.ai_document_processor.config import ai_config
from services.ai_document_processor.policy_indexer import PolicyIndexer

logger = logging.getLogger(__name__)


@dataclass
class ClaimItem:
    """Represents a single item in a claim"""
    description: str
    code: Optional[str]
    amount: float
    date: str
    provider: Optional[str]
    quantity: int = 1


@dataclass
class ReimbursementCalculation:
    """Represents the reimbursement calculation for a claim item"""
    claim_item: ClaimItem
    coverage_rate: float
    covered_amount: float
    deductible_applied: float
    final_amount: float
    policy_reference: str
    calculation_notes: List[str]


class ClaimAnalyzer:
    """Analyzes claims against policy terms and calculates reimbursements"""
    
    def __init__(self):
        """Initialize the claim analyzer"""
        self.policy_indexer = PolicyIndexer()
        
        # Initialize Groq client
        self.groq_client = Groq(api_key=ai_config.groq_api_key) if ai_config.groq_api_key else None
        
        # Initialize Gemini if available (priority)
        if ai_config.gemini_api_key:
            genai.configure(api_key=ai_config.gemini_api_key)
            self.use_gemini = True
            self.use_openai = False
            logger.info("Using Gemini API for claim analysis")
        # Initialize OpenAI if available
        elif ai_config.openai_api_key:
            openai.api_key = ai_config.openai_api_key
            self.use_openai = True
            self.use_gemini = False
            logger.info("Using OpenAI API for claim analysis")
        else:
            self.use_openai = False
            self.use_gemini = False
            logger.info("Using Groq for claim analysis")
    
    def analyze_claim(
        self, 
        extracted_data: Dict[str, Any], 
        policy_id: str,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Main method to analyze a claim against policy terms
        
        Args:
            extracted_data: Data extracted from claim document
            policy_id: ID of the customer's policy
            customer_data: Customer information including deductible status
            
        Returns:
            Complete analysis with reimbursement calculations
        """
        logger.info(f"Analyzing claim for policy {policy_id}")
        
        # Convert extracted data to claim items
        claim_items = self._extract_claim_items(extracted_data)
        
        # Analyze each claim item
        calculations = []
        total_claimed = 0
        total_approved = 0
        
        for item in claim_items:
            # Match against policy
            policy_match = self._match_policy_coverage(item, policy_id)
            
            # Calculate reimbursement
            calculation = self._calculate_reimbursement(
                item, 
                policy_match, 
                customer_data
            )
            
            calculations.append(calculation)
            total_claimed += item.amount
            total_approved += calculation.final_amount
        
        # Generate overall justification
        justification = self._generate_justification(
            calculations,
            total_claimed,
            total_approved,
            customer_data
        )
        
        # Check for any special conditions or warnings
        warnings = self._check_special_conditions(calculations, extracted_data)
        
        return {
            "claim_items": [self._item_to_dict(item) for item in claim_items],
            "calculations": [self._calculation_to_dict(calc) for calc in calculations],
            "total_claimed": round(total_claimed, 2),
            "total_approved": round(total_approved, 2),
            "approval_rate": round((total_approved / total_claimed * 100) if total_claimed > 0 else 0, 1),
            "currency": "EUR",
            "justification": justification,
            "warnings": warnings,
            "processing_date": datetime.utcnow().isoformat(),
            "policy_id": policy_id
        }
    
    def _extract_claim_items(self, extracted_data: Dict[str, Any]) -> List[ClaimItem]:
        """Convert extracted data into structured claim items"""
        items = []
        
        # Handle different document structures
        if "servicesRendered" in extracted_data:
            # New structure from document_processor
            for service in extracted_data["servicesRendered"]:
                items.append(ClaimItem(
                    description=service.get("serviceDescription", "Unknown service"),
                    code=service.get("procedureCode"),
                    amount=float(service.get("totalPrice", 0)),
                    date=service.get("dateOfService", ""),
                    provider=extracted_data.get("providerInformation", {}).get("name"),
                    quantity=int(service.get("quantity", 1))
                ))
        elif "services" in extracted_data:
            # Old structure (backward compatibility)
            for service in extracted_data["services"]:
                items.append(ClaimItem(
                    description=service.get("description", "Unknown service"),
                    code=service.get("code"),
                    amount=float(service.get("total_price", 0)),
                    date=service.get("date", extracted_data.get("service_date", "")),
                    provider=extracted_data.get("provider", {}).get("name"),
                    quantity=int(service.get("quantity", 1))
                ))
        elif "medications" in extracted_data:
            # Prescription structure
            for med in extracted_data["medications"]:
                items.append(ClaimItem(
                    description=med.get("name", "Unknown medication"),
                    code=med.get("pzn"),
                    amount=float(med.get("price", 0)),
                    date=extracted_data.get("prescription_date", ""),
                    provider=extracted_data.get("pharmacy", {}).get("name"),
                    quantity=int(med.get("quantity", 1))
                ))
        else:
            # Fallback for simple structure
            items.append(ClaimItem(
                description=extracted_data.get("description", "Medical service"),
                code=None,
                amount=float(extracted_data.get("total_amount", 0)),
                date=extracted_data.get("date", ""),
                provider=extracted_data.get("provider", "Unknown")
            ))
        
        return items
    
    def _match_policy_coverage(self, item: ClaimItem, policy_id: str) -> Dict[str, Any]:
        """Match claim item against policy coverage using RAG"""
        
        # Create search query
        query = f"""
        Coverage for: {item.description}
        Medical code: {item.code if item.code else 'not specified'}
        Service type: outpatient medical service
        """
        
        # Search policy documents
        search_results = self.policy_indexer.search_policy(query, policy_id, top_k=3)
        
        if not search_results:
            logger.warning(f"No policy matches found for: {item.description}")
            return self._default_coverage()
        
        # Use LLM to interpret the policy sections
        policy_context = "\n\n".join([
            f"Section {i+1}:\n{result['text']}" 
            for i, result in enumerate(search_results)
        ])
        
        interpretation_prompt = f"""
        Based on these policy sections, determine the coverage for this medical service:
        
        Service: {item.description}
        Code: {item.code if item.code else 'not specified'}
        Amount: €{item.amount}
        
        Policy sections:
        {policy_context}
        
        Extract:
        1. Coverage percentage (0-100)
        2. Deductible amount if mentioned
        3. Any specific conditions or exclusions
        4. Annual or per-case limits
        
        Return as JSON with these fields:
        {{
            "coverage_percentage": number,
            "deductible": number or null,
            "conditions": [],
            "exclusions": [],
            "annual_limit": number or null,
            "covered": boolean,
            "reason": "brief explanation"
        }}
        """
        
        try:
            if self.use_gemini:
                model = genai.GenerativeModel(ai_config.gemini_llm_model)
                response = model.generate_content(
                    f"You are an insurance policy expert. Analyze coverage based on policy terms and return JSON only.\n\n{interpretation_prompt}",
                    generation_config=genai.types.GenerationConfig(temperature=0.1)
                )
                # Extract JSON from response
                content = response.text
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    coverage = json.loads(json_match.group())
                else:
                    coverage = json.loads(content)
            elif self.use_openai:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an insurance policy expert. Analyze coverage based on policy terms."},
                        {"role": "user", "content": interpretation_prompt}
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"}
                )
                coverage = json.loads(response.choices[0].message.content)
            else:
                response = self.groq_client.chat.completions.create(
                    model=ai_config.groq_model,
                    messages=[
                        {"role": "system", "content": "You are an insurance policy expert. Return JSON only."},
                        {"role": "user", "content": interpretation_prompt}
                    ],
                    temperature=0.1
                )
                # Extract JSON from markdown or prose
                content = response.choices[0].message.content
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    try:
                        coverage = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse JSON from Groq response, using default coverage")
                        return self._default_coverage()
                else:
                    logger.warning("No JSON found in Groq response, using default coverage")
                    return self._default_coverage()
            
            # Add policy reference
            coverage["policy_reference"] = search_results[0]["text"][:500] + "..."
            coverage["policy_section"] = search_results[0]["metadata"].get("section_title", "Unknown section")
            
            return coverage
            
        except Exception as e:
            logger.error(f"Error interpreting policy: {e}")
            return self._default_coverage()
    
    def _default_coverage(self) -> Dict[str, Any]:
        """Return default coverage when policy matching fails"""
        return {
            "coverage_percentage": 80,  # Conservative default
            "deductible": 50,
            "conditions": ["Unable to find specific policy terms - using standard coverage"],
            "exclusions": [],
            "annual_limit": None,
            "covered": True,
            "reason": "Default coverage applied",
            "policy_reference": "Standard policy terms applied",
            "policy_section": "Default"
        }
    
    def _calculate_reimbursement(
        self,
        item: ClaimItem,
        policy_coverage: Dict[str, Any],
        customer_data: Dict[str, Any]
    ) -> ReimbursementCalculation:
        """Calculate reimbursement for a claim item"""
        
        calculation_notes = []
        
        # Check if item is covered
        if not policy_coverage.get("covered", True):
            calculation_notes.append(f"Service not covered: {policy_coverage.get('reason', 'Excluded by policy')}")
            return ReimbursementCalculation(
                claim_item=item,
                coverage_rate=0,
                covered_amount=0,
                deductible_applied=0,
                final_amount=0,
                policy_reference=policy_coverage.get("policy_reference", ""),
                calculation_notes=calculation_notes
            )
        
        # Get coverage rate
        coverage_rate = policy_coverage.get("coverage_percentage", 80) / 100
        calculation_notes.append(f"Coverage rate: {coverage_rate * 100}%")
        
        # Calculate covered amount
        covered_amount = item.amount * coverage_rate
        calculation_notes.append(f"Covered amount: €{item.amount} × {coverage_rate * 100}% = €{covered_amount:.2f}")
        
        # Apply deductible
        deductible = policy_coverage.get("deductible") or 0
        if isinstance(deductible, dict):
            deductible = deductible.get("amount", 0) or 0
        deductible = float(deductible) if deductible else 0
        remaining_deductible = max(0, deductible - customer_data.get("deductible_used_this_year", 0))
        
        deductible_applied = min(remaining_deductible, covered_amount)
        after_deductible = covered_amount - deductible_applied
        
        if deductible_applied > 0:
            calculation_notes.append(f"Deductible applied: €{deductible_applied:.2f}")
            calculation_notes.append(f"Remaining annual deductible: €{max(0, remaining_deductible - deductible_applied):.2f}")
        
        # Check annual limits
        annual_limit = policy_coverage.get("annual_limit")
        if annual_limit and annual_limit != "null":
            if isinstance(annual_limit, dict):
                annual_limit = annual_limit.get("amount")
            annual_limit = float(annual_limit) if annual_limit else None
            
        if annual_limit:
            used_this_year = customer_data.get("claims_paid_this_year", 0)
            remaining_limit = max(0, annual_limit - used_this_year)
            
            if after_deductible > remaining_limit:
                calculation_notes.append(f"Annual limit applied: €{remaining_limit:.2f} remaining of €{annual_limit}")
                final_amount = remaining_limit
            else:
                final_amount = after_deductible
        else:
            final_amount = after_deductible
        
        # Apply any special conditions
        for condition in policy_coverage.get("conditions", []):
            calculation_notes.append(f"Condition: {condition}")
        
        return ReimbursementCalculation(
            claim_item=item,
            coverage_rate=coverage_rate,
            covered_amount=round(covered_amount, 2),
            deductible_applied=round(deductible_applied, 2),
            final_amount=round(final_amount, 2),
            policy_reference=policy_coverage.get("policy_reference", ""),
            calculation_notes=calculation_notes
        )
    
    def _generate_justification(
        self,
        calculations: List[ReimbursementCalculation],
        total_claimed: float,
        total_approved: float,
        customer_data: Dict[str, Any]
    ) -> str:
        """Generate human-readable justification for the claim decision"""
        
        justification_parts = [
            f"Claim Analysis Summary",
            f"=" * 50,
            f"",
            f"Total Claimed: €{total_claimed:.2f}",
            f"Total Approved: €{total_approved:.2f}",
            f"Approval Rate: {(total_approved/total_claimed*100) if total_claimed > 0 else 0:.1f}%",
            f"",
            f"Detailed Breakdown:",
            f"-" * 30
        ]
        
        for i, calc in enumerate(calculations, 1):
            justification_parts.extend([
                f"",
                f"{i}. {calc.claim_item.description}",
                f"   Amount Claimed: €{calc.claim_item.amount:.2f}",
                f"   Coverage Rate: {calc.coverage_rate * 100:.0f}%",
                f"   Deductible Applied: €{calc.deductible_applied:.2f}",
                f"   Amount Approved: €{calc.final_amount:.2f}",
                f"   ",
                f"   Calculation Details:"
            ])
            
            for note in calc.calculation_notes:
                justification_parts.append(f"   • {note}")
            
            if calc.policy_reference:
                justification_parts.extend([
                    f"   ",
                    f"   Policy Reference:",
                    f"   \"{calc.policy_reference[:200]}...\""
                ])
        
        # Add customer status
        justification_parts.extend([
            f"",
            f"Customer Status:",
            f"- Annual Deductible Used: €{customer_data.get('deductible_used_this_year', 0):.2f}",
            f"- Claims Paid This Year: €{customer_data.get('claims_paid_this_year', 0):.2f}"
        ])
        
        return "\n".join(justification_parts)
    
    def _check_special_conditions(
        self, 
        calculations: List[ReimbursementCalculation],
        extracted_data: Dict[str, Any]
    ) -> List[str]:
        """Check for any special conditions or warnings"""
        warnings = []
        
        # Check for high-value claims
        total_amount = sum(calc.claim_item.amount for calc in calculations)
        if total_amount > 5000:
            warnings.append("High-value claim - may require additional review")
        
        # Check for multiple providers
        providers = set(calc.claim_item.provider for calc in calculations if calc.claim_item.provider)
        if len(providers) > 3:
            warnings.append(f"Multiple providers ({len(providers)}) - verify all services related")
        
        # Check for missing documentation
        if extracted_data.get("missing_fields"):
            warnings.append(f"Missing information: {', '.join(extracted_data['missing_fields'])}")
        
        # Check for excluded items
        excluded_items = [
            calc.claim_item.description 
            for calc in calculations 
            if calc.final_amount == 0 and calc.claim_item.amount > 0
        ]
        if excluded_items:
            warnings.append(f"Excluded items: {', '.join(excluded_items[:3])}")
        
        return warnings
    
    def _item_to_dict(self, item: ClaimItem) -> Dict[str, Any]:
        """Convert ClaimItem to dictionary"""
        return {
            "description": item.description,
            "code": item.code,
            "amount": item.amount,
            "date": item.date,
            "provider": item.provider,
            "quantity": item.quantity
        }
    
    def _calculation_to_dict(self, calc: ReimbursementCalculation) -> Dict[str, Any]:
        """Convert ReimbursementCalculation to dictionary"""
        return {
            "item": self._item_to_dict(calc.claim_item),
            "coverage_rate": calc.coverage_rate,
            "covered_amount": calc.covered_amount,
            "deductible_applied": calc.deductible_applied,
            "final_amount": calc.final_amount,
            "calculation_notes": calc.calculation_notes,
            "policy_reference": calc.policy_reference[:200] + "..." if len(calc.policy_reference) > 200 else calc.policy_reference
        }


# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = ClaimAnalyzer()
    
    # Example extracted data
    extracted_data = {
        "provider": {"name": "Dr. Schmidt Medical Center"},
        "services": [
            {
                "description": "General consultation",
                "code": "01010",
                "total_price": 85.00,
                "date": "2024-01-15"
            },
            {
                "description": "Blood test",
                "code": "02100",
                "total_price": 45.50,
                "date": "2024-01-15"
            }
        ]
    }
    
    # Example customer data
    customer_data = {
        "customer_id": "CUST-123456",
        "deductible_used_this_year": 25.00,
        "claims_paid_this_year": 500.00
    }
    
    # Analyze claim
    result = analyzer.analyze_claim(
        extracted_data=extracted_data,
        policy_id="HALLESCHE_NK_SELECT_S",
        customer_data=customer_data
    )
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
