# Visual-Combination-Lock

### How to Run
Run ```python upgradepasscode.py```

You will then be prompted with instructions to input images of hand gestures taken against a black background. The program will continue until it detects an image with the [End] gesture. After termination it will analyze the input images to see if the combination of gestures create a passcode that is accepted by the system. The program will output whether or not the code was accepted


### Sample Inputs
![Alt text](./sampleinputfail.png?raw=true "Title")
![Alt text](./sampleinputsuccess.png?raw=true "Title")


### Image Processing
The input images are turned into binary images, then gestures are detected using contour analysis.
![Alt text](./sampleprocessedimgs.png?raw=true "Title")
