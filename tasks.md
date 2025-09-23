```markdown
# AI Insurance Claims Platform MVP — Step-by-Step Task Plan

Each task is intentionally *small, testable, and focused on one concern.*  
**Order tasks sequentially, testing after each.**

---

## Project Setup

1. **Initialize Project Repo**
    - Start: Open terminal.
    - End: Next.js app scaffolded (`npx create-next-app`), Git initialized.

2. **Install Required Packages**
    - Start: In project directory.
    - End: All needed packages installed (`@supabase/supabase-js`, TypeScript, Tailwind).

---

## Supabase Setup

3. **Create Supabase Project**
    - Start: Log into Supabase.
    - End: New project created, credentials ready.

4. **Configure .env.local for Supabase**
    - Start: Copy API keys from Supabase dashboard.
    - End: `.env.local` has `SUPABASE_URL` and `SUPABASE_ANON_KEY`.

---

## Basic Frontend & Supabase Client

5. **Add Tailwind and Global Styles**
    - Start: Create Tailwind config, import in `src/styles/`.
    - End: Tailwind classes render in app.

6. **Setup Supabase Client (`supabaseClient.ts`)**
    - Start: In `src/services/`.
    - End: File exports a configured Supabase client using env vars.

---

## Auth: User Registration/Login

7. **Implement Registration Page**
    - Start: Create UI at `/auth/register/page.tsx`.
    - End: Submits email+password via Supabase, error/success visibly displayed.

8. **Implement Login Page**
    - Start: Create UI at `/auth/login/page.tsx`.
    - End: User can login; failures show feedback.

9. **Test Authentication Flow**
    - Start: Attempt registration and login.
    - End: User sees correct state, protected routes inaccessible if not logged in.

---

## Claims Database

10. **Create "claims" Table in Supabase**
    - Start: Via Supabase SQL editor.
    - End: Table with fields: id, user_id, status, data, created_at.

11. **Setup Basic Row Level Security**
    - Start: Enable RLS, add policy (user: only see/modify own claims).
    - End: Unprivileged users can't access others’ claims.

---

## Claims Feature — User Side

12. **Add Claims List Page (`/claims/page.tsx`)**
    - Start: Scaffold out UI.
    - End: Page lists user's existing claims.

13. **Hook Up Claim List to Supabase**
    - Start: Fetch via Supabase on load.
    - End: List renders live claim data for logged-in user.

14. **Test Claim Listing**
    - Start: Add/test claims in DB, check matching list in UI.
    - End: Only owns claims, never others’.

15. **Create Claim Submission Page**
    - Start: Scaffold `/claims/new/page.tsx` with simple form.
    - End: Submits new claim data to Supabase table.

16. **Test Claim Submission**
    - Start: Fill form, submit.
    - End: Claim visible in user’s claims list.

---

## Claims Feature — Admin Side

17. **Create Admin Route & Auth Guard**
    - Start: Set up `/admin/`, restrict with admin user check.
    - End: Unauthorized users are redirected or blocked.

18. **Admin: Claim Review List**
    - Start: List all claims for admin review (`/admin/page.tsx`).
    - End: All claims (from all users) visible to admin.

19. **Admin: Row Actions**
    - Start: Add "Approve"/"Reject" buttons beside each claim.
    - End: Buttons mutate Supabase status field.

20. **Test Admin Actions**
    - Start: Approve/reject a claim.
    - End: Status updates reflected in user list.

---

## State & Context

21. **Add Auth Context & Provider**
    - Start: In `/context/`, provide user auth/session.
    - End: Context makes user info available at all app levels.

22. **Set Up Claims Context or Store**
    - Start: Create `ClaimsProvider` or `useClaimsStore`.
    - End: Global state for quick cache/UI updates.

---

## Utilities & Middleware

23. **Add Protected Route Middleware**
    - Start: Add logic to restrict unauthenticated/unauthorized users.
    - End: Access blocked to protected/admin pages unless authorized.

---

## UX/General

24. **Add Success/Error Toast Notifications**
    - Start: Scaffold simple notification/toast component.
    - End: Actions (create claim, login, etc.) show visible feedback.

25. **Add App Layout with Navigation**
    - Start: Basic layout with nav links for user/admin routes.
    - End: Pages share main layout/look+feel.

---

## Final MVP Testing

26. **Test With New Users**
    - Start: Register/login with another account.
    - End: Only own claims visible, cannot access admin unless promoted.

27. **Test End-to-End Claim Flow**
    - Start: Register, submit claim, review claim as admin, claim is approved/rejected, status visible to user.
    - End: Full basic loop works as intended.

---

> Each task is atomic, testable, and focused.  
> MVP can be expanded further with AI/automation, but this baseline supports user management, claims CRUD, roles, and feedback.
```

[1](https://devsquad.com/blog/saas-mvp)
[2](https://boilerplatelist.com/collections/top-next-js-saas-boilerplates/)
[3](https://dev.to/mrsupercraft/introduction-to-building-a-micro-saas-with-nextjs-4j40)
[4](https://dev.to/nadim_ch0wdhury/full-stack-saas-project-management-software-development-418o)
[5](https://www.reddit.com/r/nextjs/comments/13gm2zb/best_saas_stack_and_template_for_building_quick/)
[6](https://newsletter.aimvpbuilders.com/p/how-i-set-up-supabase-mcp-inside-cursor-step-by-step)
[7](https://www.descope.com/blog/post/nextjs-supabase-descope)
[8](https://www.fiverr.com/abbasimran_007/build-your-ai-saas-mvp-with-nextjs-and-react)
[9](https://chat2db.ai/resources/blog/set-up-supabase-mcp-server)
[10](https://clerk.com/blog/nextjs-supabase-clerk)
[11](https://devdocs.hashnode.dev/building-saas-mvps-with-bunjs-and-nextjs-a-fast-and-efficient-approach)
[12](https://supabase.com/docs/guides/getting-started/mcp)
[13](https://supertokens.com/blog/how-to-integrate-clerk-with-supabase)
[14](https://www.linkedin.com/posts/run-h_i-built-a-nextjs-saas-starter-kit-to-save-activity-7278798102008905728-LX3A)
[15](https://www.strv.com/blog/supabase-authentication-a-comprehensive-guide-for-your-mvp)
[16](https://makerkit.dev/docs/next-supabase-turbo/going-to-production/checklist)
[17](https://supabase.com/docs/guides/getting-started/tutorials/with-expo-react-native)
[18](https://www.reddit.com/r/Supabase/comments/184hs8d/supabase_next_js_14_role_based_access_control/)
[19](https://www.youtube.com/watch?v=zOfdzKEsWcA)
[20](https://supabase.com/docs/guides/database/postgres/custom-claims-and-role-based-access-control-rbac)
