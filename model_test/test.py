import tensorflow as tf
import tensorflow_hub as hub

model = hub.load("models\movenet_multipose_lightning_1")
movenet = model.signatures['serving_default']

