from enum import Enum


class CompilationMode(Enum):
    NONE = 'NONE'  # No compilation
    DEFAULT = 'DEFAULT'  # Use default backend  
    INDUCTOR = 'INDUCTOR'  # Use inductor backend
    TRITON = 'TRITON'  # Use Triton backend
    AOT_EAGER = 'AOT_EAGER'  # Use AOT eager mode
    
    def __str__(self):
        return self.value
    
    def enabled(self) -> bool:
        return self != CompilationMode.NONE
