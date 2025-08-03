class PlaicubeException(Exception):
    """Base exception for Plaicube API"""
    pass

class PipelineException(PlaicubeException):
    """Pipeline related exceptions"""
    pass

class ServiceException(PlaicubeException):
    """Service related exceptions"""
    pass

class ConfigurationException(PlaicubeException):
    """Configuration related exceptions"""
    pass

class ValidationException(PlaicubeException):
    """Validation related exceptions"""
    pass 