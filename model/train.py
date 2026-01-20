from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="model/data.yaml",
    epochs=50,
    imgsz=360,
    batch=16,
    device=0,
    name="50-epochs",
)

model.val()