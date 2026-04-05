# Whiteboard Cleanup Prompt

**Model:** Fal AI Nano Banana 2 (image-to-image)  
**Endpoint:** `fal-ai/nano-banana-2/edit`  
**Version:** 1.0

## Prompt

> Take this whiteboard photograph and convert it into a beautiful and polished graphic featuring clear labels and icons. Remove the physical whiteboard, markers, frame, and any background elements -- output only the diagram on a clean white background. Correct any perspective distortion so the output appears as a perfectly straight-on, top-down view regardless of the angle the original photo was taken from. Preserve all the original content, text, and diagrams. When reading handwritten text, infer the correct spelling of technical terms, product names, and proper nouns rather than transcribing handwriting literally (e.g. "Proxmox" not "Proxknox", "Kubernetes" not "Kubernites"). Keep the user's handwriting style and character but make it more legible and well-organized. The result should be a fully representative version of the whiteboard content that is much more visually attractive and easy to understand than the original photo.

## Settings

| Parameter | Value |
|-----------|-------|
| Output format | PNG |
| Resolution | 1K |
| Variants | 1 |

## Design Notes

- The prompt explicitly instructs removal of the physical whiteboard and surrounding environment so the output is a clean diagram, not a photo of a whiteboard.
- Handwriting style is preserved intentionally -- the goal is to clean up, not to replace hand-drawn content with generic fonts or shapes.
- Legibility is prioritized: text and labels should be easier to read than the original photo while retaining the author's character.
- All original content (text, arrows, boxes, diagrams) must be preserved -- nothing should be dropped or summarized.
- Perspective correction ensures the output is a clean, straight-on view even if the original photo was taken at an angle.
