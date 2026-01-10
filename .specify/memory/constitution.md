<!--
SYNC IMPACT REPORT
==================
Version Change: 1.0.0 → 1.1.0
Modified Principles:
  - V. Security & Data Protection (EXPANDED - added sensitive data protection rules)

Added Standards:
  - Package Management (NEW - UV requirement)
  - Git Security (NEW - sensitive files protection)

Templates Status:
  - ✅ .specify/templates/plan-template.md (aligned)
  - ✅ .specify/templates/spec-template.md (aligned)
  - ✅ .specify/templates/tasks-template.md (aligned)

Follow-up TODOs: None
-->

# Cat Canteen V3 Constitution

## Core Principles

### I. Spec-First Development
All features and changes must be specified before implementation. Each specification must include:
- Clear problem statement and goals
- Detailed requirements and acceptance criteria
- Design decisions and rationale
- Success metrics

**Rationale**: Prevents scope creep, ensures stakeholder alignment, and creates a single source of truth for what we're building and why.

### II. Clear Documentation
Every component, API, and non-trivial function must have documentation that explains:
- Purpose and responsibilities
- Input/output contracts
- Usage examples
- Edge cases and limitations

**Rationale**: Enables team collaboration, reduces onboarding time, and makes code maintainable long-term.

### III. Test-Driven Development (NON-NEGOTIABLE)
Tests must be written before implementation code. The workflow is:
1. Write failing tests based on specifications
2. Get test approval from stakeholders
3. Implement minimum code to pass tests
4. Refactor while keeping tests green

**Rationale**: Ensures code correctness, prevents regressions, and validates that requirements are testable and clear.

### IV. Code Quality & Maintainability
All code must prioritize:
- Simplicity over cleverness (YAGNI - You Aren't Gonna Need It)
- Self-documenting code with clear naming
- Single Responsibility Principle
- DRY (Don't Repeat Yourself) when abstraction adds clarity

**Rationale**: Reduces technical debt, makes debugging easier, and improves long-term development velocity.

### V. Security & Data Protection (NON-NEGOTIABLE)
Security requirements are mandatory for all features:
- Input validation at all system boundaries
- Protection against OWASP Top 10 vulnerabilities
- Secure credential and sensitive data handling
- Regular security reviews for critical paths
- **敏感資訊絕對禁止上傳至 GitHub**，包括但不限於：
  - API keys, tokens, passwords
  - 資料庫連線字串
  - 私鑰檔案 (.pem, .key, etc.)
  - 環境變數檔案 (.env, .env.local, etc.)
  - 設定檔中的敏感資料
- 必須使用 .gitignore 防止敏感檔案被追蹤
- 使用環境變數或安全的密鑰管理服務儲存敏感資訊

**Rationale**: Protects user data, maintains system integrity, prevents costly security incidents, and avoids credential leaks that could lead to system compromise.

## Technical Standards

### Package Management (NON-NEGOTIABLE)
All Python dependencies MUST be managed through UV:
- 使用 `uv` 作為唯一的套件管理工具
- 所有套件安裝必須使用 `uv pip install` 或 `uv tool install`
- 依賴項必須記錄在 `pyproject.toml` 或 `requirements.txt`
- 禁止使用 pip、conda 或其他套件管理工具（除非有明確技術理由並經批准）
- 虛擬環境必須使用 `uv venv` 創建

**Rationale**: UV provides faster, more reliable dependency resolution and installation. Standardizing on one tool prevents version conflicts and ensures reproducible builds across all environments.

### Code Standards
All code must follow established patterns and conventions:
- Consistent code style (enforced via linters/formatters)
- Error handling with clear, actionable error messages
- Logging for debugging and monitoring (info, warning, error levels)
- Version control with meaningful commit messages

### Git Security
Repository must maintain secure practices:
- `.gitignore` 必須包含所有敏感檔案模式
- 提交前必須檢查是否包含敏感資訊
- 發現敏感資訊已提交時，必須立即使用 git filter-branch 或 BFG Repo-Cleaner 移除
- 定期審查 .gitignore 確保涵蓋所有敏感檔案類型

### Technology Decisions
Technology decisions must be documented with:
- Technical justification
- Alternative options considered
- Trade-offs and limitations
- Migration path if replacing existing tech

## Development Workflow

### Review & Approval Process
1. Specification review and approval before implementation
2. Code review required for all changes
3. All tests must pass before merge
4. Breaking changes require explicit migration plans

### Quality Gates
- Unit test coverage minimum: 80%
- Integration tests for all API endpoints
- Performance benchmarks for critical paths
- Security scan for dependency vulnerabilities

### Deployment Standards
- Staging environment testing required
- Rollback plan documented for major changes
- Feature flags for risky deployments
- Post-deployment monitoring and validation

## Governance

This constitution supersedes all other development practices and policies. All team members must:
- Follow these principles in all work
- Raise concerns when principles are violated
- Propose amendments through documented RFC process
- Participate in quarterly compliance reviews

### Amendment Process
Constitutional changes require:
1. Written proposal with rationale and impact analysis
2. Team review and discussion period (minimum 1 week)
3. Approval from project stakeholders
4. Version bump following semantic versioning
5. Update to all dependent templates and documentation

### Compliance
- All code reviews must verify constitutional compliance
- Exceptions must be explicitly justified and documented
- Technical debt must include remediation plan and timeline
- Violations are addressed in retrospectives

**Version**: 1.1.0 | **Ratified**: 2026-01-08 | **Last Amended**: 2026-01-08
