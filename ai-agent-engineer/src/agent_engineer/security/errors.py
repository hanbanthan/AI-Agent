from agent_engineer.errors import AgentError

class SecurityError(AgentError):
    retryable = False

class PermissionDeniedError(SecurityError):
    pass

class ConfirmationRequiredError(SecurityError):
    pass

class SecurityValidationError(SecurityError):
    pass

class DataFlowViolationError(SecurityError):
    pass

