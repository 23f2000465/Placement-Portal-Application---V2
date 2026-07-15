# Milestone 2: Authentication and RBAC

Students and companies can register, all roles can log in, and protected APIs check the logged-in role. Admin registration does not exist.

Main routes: `POST /api/auth/register/student`, `POST /api/auth/register/company`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`.

Run and test commands are in the main README. The `user` table and student/company profile tables are involved.

## Simple concepts

- **Route:** URL par request receive karne wala Python function.
- **POST:** server ko data bhejta hai. **GET:** data leta hai.
- **request:** browser se aaya data. **jsonify:** Python data ko JSON response banata hai.
- **Session:** signed cookie ke through logged-in user ID yaad rakhti hai.
- **Decorator:** protected route se pehle common role check chalata hai.

## Viva questions

1. Why no admin registration? Admin must be predefined.
2. Why hash passwords? Actual passwords are never stored.
3. What is RBAC? Each role receives only its permitted APIs.
4. Why backend authorization? Hidden frontend buttons can be bypassed.
5. What is a session? Server-signed login state stored through a cookie.

Live changes: increase minimum password length; add a contact validation rule.
