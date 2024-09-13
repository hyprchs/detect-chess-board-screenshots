# Finetuning process

Note 9/12/24: Most of the code in this folder was trying to fine-tune YOLO-World, which I gave up on because it seemed too complicated and poorly documented. I ended up using YOLOv8 instead which was much easier. 

1. Make sure the class captions are correct at `./class_captions.json`. It looks like they should be a list of lists, where each inner list contains strings that all represent the same class.

1. Generate the text embeddings for these strings
```sh
cd YOLO-World
python tools/generate_text_prompts.py --text ../fine_tuning/class_captions.json --out ../fine_tuning/output.npy
```

1. Reparameterize the model and save to a new checkpoint. My understanding is that this applies the text embeddings we just created into the parameters of the existing model so it doesn't have to recalculate them on each pass during inference.
```sh

```