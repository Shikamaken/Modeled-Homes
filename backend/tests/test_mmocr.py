from mmocr.apis.inferencers.mmocr_inferencer import MMOCRInferencer

# Initialize MMOCRInferencer with text detection and recognition
mmocr = MMOCRInferencer(det='DBNet', rec='SAR')

print("MMOCRInferencer initialized successfully.")