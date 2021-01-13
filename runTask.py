import os
import fnmatch
from psychopy import visual, gui, data, core, event, logging, info
from psychopy.constants import *
homeDir = '/home/vman/Dropbox/PostDoctoral/gitRepos/prob_reversal'
# Ensure that relative paths start from the same directory as this script
os.chdir(homeDir)
outDir = homeDir + os.sep + 'Output'
stimDir = homeDir + os.sep + 'Images'
payDir = homeDir + os.sep + 'PayOut'
# Create directories if they don't exist
if not os.path.exists(outDir):
    os.mkdir(outDir)
if not os.path.exists(stimDir):
    os.mkdir(stimDir)
if not os.path.exists(payDir):
    os.mkdir(payDir)


# Add dependencies
from config import *
from runInstruct import *
from runPract import *
from initTask import *
from runBandit import *

## Experiment start ##
# Store info about the experiment session
# Reference: allowable inputs
# SubNo. - has to be digits
# Version - test or debug or pract
# BSCond - rl or hm
# Modality - behaviour or fMRI
check = 0
while check == 0:
    expName = 'Task'  # from the Builder filename that created this script
    expInfo = {'SubNo': 999,
               'Version': 'test',
               'BSCond': 'rl',
               'Modality': 'fMRI',
               'doInstruct': True,
               'doPract': True,
               'doTask': True}
    dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
    if dlg.OK == False:
        print('User Cancelled')  # user pressed cancel
        core.wait(3)
        core.quit()
    # Check to see there's no existing subject ID - if there is, repeat this dialogue box
    exist = False
    for file in os.listdir(outDir):
        if fnmatch.fnmatch(file, '*' + str(expInfo['SubNo']) + '*'):
            exist = True
    if (exist):
        check = 0
        print('That file already exists, try another subject number!')
    else:
        check = 1
expInfo.update({'date': data.getDateStr(),  # add a simple timestamp
                'expName': expName,
                'homeDir': homeDir,
                'outDir': outDir,
                'stimDir': stimDir,
                'payDir': payDir})
# Set up between-subject counterbalance
expInfo = dict2class(counterbalance(expInfo))  # output is given by expInfo.sub_cb
#####  Task Section  #####
taskClock = core.Clock()
# Initialize general parameters
[screen, dispInfo, taskInfo, taskObj, keyInfo] = initTask(expInfo)
instruct_initInfo = dict2class(initInstruct(expInfo, taskInfo, taskObj))
practInfo = dict2class(initPract(expInfo, taskInfo))


if __name__ == "__main__":
    # Run instructions
    if (expInfo.doInstruct):
        runInstruct(expInfo, dispInfo, taskInfo, taskObj, keyInfo, instruct_initInfo)
    if (expInfo.doPract):
        runPract(dispInfo, taskInfo, taskObj, keyInfo, practInfo)
    # Run the task
    if (expInfo.doTask):
        runBandit(expInfo, dispInfo, taskInfo, taskObj, keyInfo)
    # Close screen after experiment ends
    screen.close()
    # Print out the final payment amount across the session(s)
    sessionPay = 0
    for sI in np.arange(taskInfo.numSessions):
        sessionPay = sessionPay + np.sum(taskInfo.sessionInfo[sI].payOut)
    print('Payment: ' + str(sessionPay))
