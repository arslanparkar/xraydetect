print("[xray] Importing libraries")
from typing import Optional

from skimage.io import imread
from torch import from_numpy, no_grad
from torchvision.transforms import Compose
from torchxrayvision import datasets, models

from . import exceptions


class XrayScanner:
    def __init__(self, weights: Optional[str] = "all") -> None:
        """
        Runs a neural network from a pretrained model.

        Note: This does not use GPU Acceleration currently.

        Args:
            weights: Pre trained weights to use. Defaults to "all".
        """

        print("[xray] Loading model")
        self.model = models.DenseNet(weights=weights)

    def scan_xray(self, image: bytes) -> dict:
        """
        Scans an image using the model which was loaded.

        Args:
            image: Path to the image. Ideally should be absolute.

        Returns:
            dict: Dictionary containing predictions.
        """
        print("[xray] Opening image")
        image = imread(image, plugin="imageio")
        image = datasets.normalize(image, 255)

        print("[xray] Running image correction")
        if len(image.shape) < 2:
            raise exceptions.InvalidDimensions("Dimensions is lower than 2.")
            return

        elif len(image.shape) > 2:
            image = image[:, :, 0]

        image = image[None, :, :]  # Add color channel
        image = Compose([datasets.XRayCenterCrop(), datasets.XRayResizer(224)])(image)

        print("[xray] Predicting abnormalities")
        with no_grad():
            image = from_numpy(image).unsqueeze(0)
            prediction = self.model(image).cpu()
            prediction = dict(
                zip(
                    (pathology.replace("_", " ") for pathology in datasets.default_pathologies),
                    prediction[0].detach().numpy()
                   )
            )
            prediction = dict(sorted(prediction.items(), key=lambda x:x[1])[::-1])
            return prediction
