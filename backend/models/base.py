# base.py model wrapper interface placeholder
"""
WHAT: This file defines the abstract base class (interface) for all AI models in the pipeline.
WHY: By enforcing a strict contract (initialize, generate, cleanup), we ensure that the orchestration 
     layer (pipeline.py) does not need to know the implementation details of any specific model. 
     It simply loops through the models and calls these standard methods. This abstraction allows us 
     to swap out an image generator or an audio generator without breaking the pipeline logic.
HOW: It uses Python's built-in `abc` (Abstract Base Classes) module. Any class inheriting from 
     `BaseModel` MUST implement the decorated methods, otherwise Python will throw an error at runtime.
"""

from abc import ABC, abstractmethod
from typing import Any

class BaseModel(ABC):
    """
    Abstract interface for all AI models in the Multiverse AI Studio pipeline.
    
    Every model wrapper (LLM, Image, Depth, Audio, Video) must inherit from this class
    and provide concrete implementations for these three methods.
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        WHAT: Loads the model weights into memory (CPU/GPU) and prepares it for inference.
        WHY: Models are heavy. We want granular control over exactly when a model is loaded 
             into VRAM to prevent Out-Of-Memory (OOM) errors.
        HOW: Implementations will typically instantiate Hugging Face pipelines or 
             Diffusers pipelines here using the config.DEVICE.
        """
        pass

    @abstractmethod
    def generate(self, **kwargs) -> Any:
        """
        WHAT: Executes the core inference logic of the model.
        WHY: This is where the actual AI work happens (e.g., text -> text, text -> image, image -> depth).
             Using `**kwargs` allows flexible input arguments, as different models require 
             different inputs (e.g., prompt, image, audio_length).
        HOW: The pipeline layer will pass the output of the previous model as kwargs into this method.
             Returns the generated asset (text, PIL Image, audio tensor, or video frames).
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        WHAT: Unloads the model from memory and clears the GPU cache.
        WHY: In a chained pipeline of 5 heavy AI models, we cannot keep all models in VRAM 
             simultaneously on consumer hardware. We must aggressively free memory after a 
             model finishes its task.
        HOW: Implementations should delete the model instance (e.g., `del self.pipe`) and 
             call `torch.cuda.empty_cache()`.
        """
        pass 