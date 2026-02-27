# Judge Preparation — Likely Questions & Answers

## "Why did you choose imitation learning over RL?"
Imitation learning from human demonstrations converges reliably within a 48-hour hackathon.
RL requires a well-designed reward function and many environment interactions — both hard
to get right under time pressure. We can fine-tune with RL later.

## "How did you ensure data quality?"
- Reviewed every 10th episode during collection
- Discarded failed grasps immediately
- Varied object position across at least 5 different locations
- Maintained consistent lighting throughout collection

## "How did you handle the sim-to-real gap?"
We worked entirely in the real world — all data was collected on the actual robot.
There is no sim-to-real gap because there was no simulation.

## "What is the role of the Jetson?"
Onboard inference: the Jetson runs the trained policy at 30 Hz using TensorRT,
without needing a network connection. The cloud GPU was only used for training.

## "Why ACT (Action Chunking Transformer)?"
ACT predicts a chunk of future actions at once (100 steps), which reduces the
compounding error of autoregressive policies. It performs well on manipulation
tasks with visual input and is natively supported by LeRobot.

## "What would you do with more time?"
1. Collect more diverse episodes for better generalisation
2. Fine-tune with RL to improve grasping success rate
3. Add depth sensing for more robust 3D localisation
4. Deploy on more object types (sort by colour)

## "What was the hardest challenge?"
(Fill in during the event — be honest, judges respect candour)

## Demo talking points
- Show the robot navigating autonomously to the object
- Point out the camera feed on the screen
- Mention the inference speed (XX ms per step)
- Mention the safety features (e-stop, velocity limits)
