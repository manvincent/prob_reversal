from psychopy import visual, gui, data, core, event, logging, info
from psychopy.constants import *
import numpy as np # whole numpy lib is available, prepend 'np.'
from initTask import *

def initPract(expInfo, taskInfo):
    # task properties
    numPractTrials = 6
    # Randomise stimulus order for practice
    pract_stim1_left = np.random.binomial(1, 0.5, numPractTrials).astype(bool)
    # Outcome
    pract_outMag_left = np.empty(numPractTrials, dtype=object)
    pract_outMag_right = np.empty(numPractTrials, dtype=object)
    # Assign fixed outcomes to practice trials
    pract_pWin = np.concatenate([np.tile(1, numPractTrials//2), np.tile(0, numPractTrials//2)])
    pract_outMag = np.tile(taskInfo.outMag, numPractTrials // len(taskInfo.outMag))
    combined = list(zip(pract_pWin, pract_outMag))
    np.random.shuffle(combined)
    pract_pWin, pract_outMag = zip(*combined)
    for idx, mag in enumerate(pract_outMag):
        if (pract_pWin[idx]):
            pract_outMag_left[idx] = pract_outMag_right[idx] = TrialObj(taskInfo,
                                                                        type='out',
                                                                        pathToFile=expInfo.stimDir + os.sep + 'cb_' + str(expInfo.sub_cb) + os.sep + 'gain_' + str(mag))
        else:
            pract_outMag_left[idx] = pract_outMag_right[idx] = TrialObj(taskInfo,
                                                                        type='out',
                                                                        pathToFile=expInfo.stimDir + os.sep + 'cb_' + str(expInfo.sub_cb) + os.sep + 'loss_' + str(mag))
    return dict(numPractTrials=numPractTrials,
                pract_stim1_left=pract_stim1_left,
                pract_outMag_left=pract_outMag_left,
                pract_outMag_right=pract_outMag_right,
                pract_pWin=pract_pWin,
                pract_outMag=pract_outMag)
    
def runPract(dispInfo, taskInfo, taskObj, keyInfo, practInfo):
    # Show practice start screen
    while True:
        taskObj.practStart.draw()
        taskObj.screen.flip()
        response = event.waitKeys(keyList=[keyInfo.instructDone,'escape'])
        if keyInfo.instructDone in response:
            break
        elif 'escape' in response:
            core.wait(1)
            core.quit()
    # Proceed to trials
    practClock = core.Clock()
    for tI in range(practInfo.numPractTrials):
        trialStart = practClock.getTime()
        # Run the trial
        runPractTrial(tI, dispInfo, taskInfo, taskObj, keyInfo, practInfo, practClock)
        taskObj.ITI.complete()
        # Print trial timestamp
        print('Trial time ' + str(tI) + ': ' + str(practClock.getTime() - trialStart))
    # Show practice end screen
    while True:
        taskObj.practEnd.draw()
        taskObj.screen.flip()
        response = event.waitKeys(keyList=[keyInfo.instructDone,'escape'])
        if keyInfo.instructDone in response:
            break
        elif 'escape' in response:
            core.wait(1)
            core.quit()
    return

def runPractTrial(tI, dispInfo, taskInfo, taskObj, keyInfo, practInfo, practClock):
    jitterTime = np.random.choice(taskInfo.sessionInfo[0].jitter)
    taskObj.ITI.start(jitterTime)
    # Show start fixation
    taskObj.startFix.setAutoDraw(True)
    taskObj.screen.flip()
    taskObj.startFix.setAutoDraw(False)
    taskObj.ITI.complete()
    # Show the practice stimulus
    if (practInfo.pract_stim1_left[tI]):
        taskObj.leftStim.image=taskObj.stim1.path
        taskObj.leftResp.image=taskObj.stim1.respPath
        taskObj.rightStim.image=taskObj.stim2.path
        taskObj.rightResp.image=taskObj.stim2.respPath
    else:
        taskObj.leftStim.image=taskObj.stim2.path
        taskObj.leftResp.image=taskObj.stim2.respPath
        taskObj.rightStim.image=taskObj.stim1.path
        taskObj.rightResp.image=taskObj.stim1.respPath
    # Rescale images
    taskObj.leftStim.rescaledSize = rescaleStim(taskObj.leftStim, dispInfo.imageSize, dispInfo)
    taskObj.leftStim.setSize(taskObj.leftStim.rescaledSize)
    taskObj.leftResp.rescaledSize = rescaleStim(taskObj.leftResp, dispInfo.imageSize, dispInfo)
    taskObj.leftResp.setSize(taskObj.leftResp.rescaledSize)
    taskObj.rightStim.rescaledSize = rescaleStim(taskObj.rightStim, dispInfo.imageSize, dispInfo)
    taskObj.rightStim.setSize(taskObj.rightStim.rescaledSize)
    taskObj.rightResp.rescaledSize = rescaleStim(taskObj.rightResp, dispInfo.imageSize, dispInfo)
    taskObj.rightResp.setSize(taskObj.rightResp.rescaledSize)
    # Draw the stims
    taskObj.leftStim.setAutoDraw(True)
    taskObj.rightStim.setAutoDraw(True)
    stimOnset = practClock.getTime()
    # Flip screen and wait for response
    taskObj.screen.flip()
    response = event.clearEvents()
    while (practClock.getTime() - stimOnset) <= taskInfo.trialInfo.maxRT:
        # wait for response
        response = event.getKeys(keyList=[keyInfo.respLeft, keyInfo.respRight])

        # Process response
        if response:
            # Get response time to calculate RT below
            taskObj.ITI.start(taskInfo.trialInfo.isiTime)
            # which response was made
            if keyInfo.respLeft in response:
                # left key was pressed
                fbPosition = dispInfo.imagePosL
                # Show response-specific ISI screen
                taskObj.leftStim.setAutoDraw(False)
                taskObj.leftResp.setAutoDraw(True)
                taskObj.screen.flip()
                taskObj.leftResp.setAutoDraw(False)
                taskObj.ITI.complete()
                # Show outcome feedback
                taskObj.ITI.start(taskInfo.trialInfo.fbTime)
                taskObj.leftOut.image = practInfo.pract_outMag_left[tI].path
                taskObj.leftOut.rescaledSize = rescaleStim(taskObj.leftOut, dispInfo.imageSize, dispInfo)
                taskObj.leftOut.setSize(taskObj.leftOut.rescaledSize)
                taskObj.leftOut.setAutoDraw(True)
                taskObj.screen.flip()
                # Clear objects after presenting
                taskObj.leftOut.setAutoDraw(False)
                taskObj.rightStim.setAutoDraw(False)
                taskObj.ITI.complete()
            elif keyInfo.respRight in response:
                # right key was pressed
                fbPosition = dispInfo.imagePosR
                # Show response-specific ISI screen
                taskObj.rightStim.setAutoDraw(False)
                taskObj.rightResp.setAutoDraw(True)
                taskObj.screen.flip()
                taskObj.rightResp.setAutoDraw(False)
                taskObj.ITI.complete()
                # Show outcome feedback
                taskObj.ITI.start(taskInfo.trialInfo.fbTime)
                taskObj.rightOut.image = practInfo.pract_outMag_right[tI].path
                taskObj.rightOut.rescaledSize = rescaleStim(taskObj.rightOut, dispInfo.imageSize, dispInfo)
                taskObj.rightOut.setSize(taskObj.rightOut.rescaledSize)
                taskObj.rightOut.setAutoDraw(True)
                taskObj.screen.flip()
                # Clear objects after presenting
                taskObj.rightOut.setAutoDraw(False)
                taskObj.leftStim.setAutoDraw(False)
                taskObj.ITI.complete()
            #  Present trial-end fixation
            taskObj.ITI.start(taskInfo.trialInfo.endFixTime +
                            (taskInfo.trialInfo.maxJitter - jitterTime))
            taskObj.endFix.setAutoDraw(True)
            taskObj.screen.flip()
            taskObj.endFix.setAutoDraw(False)
            break
    if not response:
        taskObj.ITI.start(taskInfo.trialInfo.isiTime + taskInfo.trialInfo.fbTime)
        taskObj.leftStim.setAutoDraw(False)
        taskObj.rightStim.setAutoDraw(False)
        taskObj.noRespErr.setAutoDraw(True)
        taskObj.screen.flip()
        taskObj.noRespErr.setAutoDraw(False)
        taskObj.ITI.complete()
        #  Present trial-end fixation
        taskObj.ITI.start(taskInfo.trialInfo.endFixTime +
                        (taskInfo.trialInfo.maxJitter - jitterTime))
        taskObj.endFix.setAutoDraw(True)
        taskObj.screen.flip()
        taskObj.endFix.setAutoDraw(False)
    return
