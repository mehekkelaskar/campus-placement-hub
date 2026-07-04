## AI-Assisted Development

This project was built using an AI-assisted engineering workflow. AI coding agents were used for code generation, implementation, and automated test creation, while I directed the development process by defining product requirements, specifying user and admin workflows, reviewing generated code, configuring the development environment, debugging failures, validating API behavior, and conducting automated and performance testing.

The generated implementation was independently validated rather than treated as complete after code generation. The backend was tested with 87 automated tests, all of which passed successfully.

Performance testing was conducted using Locust with incremental loads of 10, 50, 100, and 200 concurrent users. At 100 concurrent users, the application processed 5,689 requests with:

- ~49.4 requests per second
- 60 ms p95 response time
- 110 ms p99 response time
- 0% request failure rate

At 200 concurrent users, the local test environment experienced HTTP 500 errors on the company-detail endpoint. This identified a performance issue for further investigation and optimization.

## AI Engineering Workflow

- Defined the product requirements, features, user roles, and expected application behavior.
- Directed AI coding agents during implementation and automated test generation.
- Reviewed and executed AI-generated code instead of treating code generation as project completion.
- Debugged generated test failures and development environment issues.
- Validated 87 automated backend tests with a 100% pass rate.
- Designed incremental load tests at 10, 50, 100, and 200 concurrent users.
- Analyzed throughput, p95/p99 latency, failure rates, and endpoint-specific failures.
- Identified the tested stability boundary of the local development environment through evidence-based performance testing.