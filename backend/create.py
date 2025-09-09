# In backend/create_model.py

import tensorflow as tf

NUM_CLASSES = 38

print("Creating a new lightweight model architecture...")

# 1. Load the base of MobileNetV2, pre-trained on ImageNet.
base_model = tf.keras.applications.MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(224, 224, 3)
)
base_model.trainable = False

# 2. Create a new model on top of the base model.
model = tf.keras.Sequential([
    base_model,
    # 3. THIS IS THE FIX: Add a GlobalAveragePooling2D layer.
    #    This layer correctly flattens the output from the base model into the
    #    single input that the final Dense layer expects.
    tf.keras.layers.GlobalAveragePooling2D(),
    
    # 4. Add our final layer.
    tf.keras.layers.Dense(NUM_CLASSES, activation='softmax')
])

# 5. Save the complete new model.
model.save("plant_disease_model.h5")

print("✅ Successfully created and saved 'plant_disease_model.h5'.")