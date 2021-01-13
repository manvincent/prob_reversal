from psychopy import visual, event, core
import numpy as np # whole numpy lib is available, prepend 'np.'
import os
from config import *


def runInstruct(expInfo, dispInfo, taskInfo, taskObj, keyInfo, instruct_initInfo):
    pages = np.arange(instruct_initInfo.instructInfo.numPages)
    # Initialize instruct page object
    instructObj = InstructPages(taskObj, dispInfo, instruct_initInfo.instructInfo, instruct_initInfo.imagePaths)
    currPage = 1
    while True:
        # Run instruction function
        if currPage == 9:
            if (expInfo.BSCond == 'rl'):
                getattr(instructObj, 'instruct_%s_rl' % currPage)()
            elif (expInfo.BSCond == 'hm'):
                getattr(instructObj, 'instruct_%s_hm' % currPage)()
            else:
                raise Exception('Error: Condition specified incorrectly')
        else:
            getattr(instructObj, 'instruct_%s' % currPage)()
        # wait for response
        if currPage == 6:
            response = event.waitKeys(keyList=[keyInfo.respLeft,'escape'])
            if keyInfo.respLeft in response:
                # Show ISI
                taskObj.rightStim.image=instructObj.rightStim_path
                taskObj.rightStim.rescaledSize = rescaleStim(taskObj.rightStim, dispInfo.imageSize, dispInfo)
                taskObj.rightStim.setSize(taskObj.rightStim.rescaledSize)
                taskObj.leftResp.image=instructObj.leftStim_respPath
                taskObj.leftResp.rescaledSize = rescaleStim(taskObj.leftResp, dispInfo.imageSize, dispInfo)
                taskObj.leftResp.setSize(taskObj.leftResp.rescaledSize)
                taskObj.rightStim.setAutoDraw(True)
                taskObj.leftResp.setAutoDraw(True)
                taskObj.screen.flip()
                taskObj.leftResp.setAutoDraw(False)
                core.wait(taskInfo.trialInfo.isiTime)
                # Show random outcome
                if (np.random.choice([True, False])):
                    taskObj.leftOut.image = taskObj.outGain[0].path
                else:
                    taskObj.leftOut.image = taskObj.outLoss[0].path
                taskObj.leftOut.rescaledSize = rescaleStim(taskObj.leftOut, dispInfo.imageSize, dispInfo)
                taskObj.leftOut.setSize(taskObj.leftOut.rescaledSize)
                taskObj.leftOut.setAutoDraw(True)
                taskObj.screen.flip()
                taskObj.leftOut.setAutoDraw(False)
                taskObj.rightStim.setAutoDraw(False)
                core.wait(taskInfo.trialInfo.fbTime)
                # Move forward a page
                currPage = min(len(pages), currPage+1)
                print('Page: ' + str(currPage))
            elif 'escape' in response:
                core.wait(1)
                core.quit()
        elif currPage == instruct_initInfo.instructInfo.numPages:
            response = event.waitKeys(keyList=[keyInfo.instructDone, 'escape'])
            if keyInfo.instructDone in response:
                break
            elif 'escape' in response:
                core.wait(1)
                core.quit()
        else:
            response = event.waitKeys(keyList=keyInfo.instructAllow)
            if keyInfo.instructPrev in response:
                # Move back a screen
                currPage = max(1,currPage-1)
                print('Page: '  + str(currPage))
            elif keyInfo.instructNext in response:
                # Move forward a screen
                currPage = min(len(pages), currPage+1)
                print('Page: ' + str(currPage))
            elif 'escape' in response:
                core.wait(1)
                core.quit()
    return



def initInstruct(expInfo, taskInfo, taskObj):
    # Specify instruction image directory
    instructDir = expInfo.stimDir + os.sep + 'instruct'

    def setImagePath(instructDir):
        # Instruction related images
        instruct_set = instructDir + os.sep + 'instruct_set.png'
        instruct_left = instructDir + os.sep + 'instruct_left.png'
        instruct_right = instructDir + os.sep + 'instruct_right.png'
        # Response related images
        resp_set = instructDir + os.sep + 'resp_set.png'
        resp_left = instructDir + os.sep + 'resp_left.png'
        resp_right = instructDir + os.sep + 'resp_right.png'
        return dict(instruct_set=instruct_set,
                    instruct_left=instruct_left,
                    instruct_right=instruct_right,
                    resp_set=resp_set,
                    resp_left=resp_left,
                    resp_right=resp_right)
    imagePaths = dict2class(setImagePath(instructDir))

    def instructParam(expInfo):
        # Number of pages
        numPages = 12
        # Randomise stimulus order for instruction
        instruct_stim1_left = np.random.binomial(1, 0.5, 1).astype(bool)[0]
        return dict(numPages=numPages,
                    instruct_stim1_left=instruct_stim1_left)
    instructInfo = dict2class(instructParam(expInfo))

    return dict(instructInfo=instructInfo,
                imagePaths=imagePaths)


class InstructPages(object):
    def __init__(self, taskObj, dispInfo, instructInfo, imagePaths):
        self.screen = taskObj.screen
        self.posHigh = [0, 0.5]
        self.posMid = [0, 0]
        self.posLow = [0, -0.5]
        self.posImage = [0, -0.25]
        self.height = 0.08
        self.color = 'black'
        self.wrapWidth = 1.8
        self.imageSize = dispInfo.imageSize
        self.imagePosL = dispInfo.imagePosL
        self.imagePosR = dispInfo.imagePosR
        # Set up navigation images
        self.posNavL = [-0.7, -0.75]
        self.posNavR = [0.7, -0.75]
        self.sizeNav = dispInfo.imageSize
        self.heightNav = self.height*(3/4)
        # Display information
        self.monitorX = dispInfo.monitorX
        self.monitorY = dispInfo.monitorY
        self.screenScaling = dispInfo.screenScaling
        # Randomly assign the left and right stims
        if (instructInfo.instruct_stim1_left):
            self.leftStim_path = taskObj.stim1.path
            self.leftStim_respPath = taskObj.stim1.respPath
            self.rightStim_path = taskObj.stim2.path
            self.rightStim_respPath = taskObj.stim2.respPath
        else:
            self.leftStim_path = taskObj.stim2.path
            self.leftStim_respPath = taskObj.stim2.respPath
            self.rightStim_path = taskObj.stim1.path
            self.rightStim_respPath = taskObj.stim1.respPath
        # Set up the paths to demo outcomes
        self.gain_path = taskObj.outGain[1].path
        self.loss_path = taskObj.outLoss[1].path
        # Set up navigation objects
        self.imagePaths = imagePaths
        self.navBack = visual.TextStim(win=self.screen,
                                       text='Press this to go back',
                                       pos=[self.posNavL[0], -0.9],
                                       height=self.heightNav,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.navForward = visual.TextStim(win=self.screen,
                                          text='Press this to go forward',
                                          pos=[self.posNavR[0], -0.9],
                                          height=self.heightNav,
                                          color=self.color,
                                          wrapWidth=self.wrapWidth)
        self.instructLeft = visual.ImageStim(win=self.screen,
                                             image=imagePaths.instruct_left,
                                             size=self.sizeNav,
                                             pos=self.posNavL)
        self.instructRight = visual.ImageStim(win=self.screen,
                                              image=imagePaths.instruct_right,
                                              size=self.sizeNav,
                                              pos=self.posNavR)
        self.navLeft = visual.TextStim(win=self.screen,
                                       text='Press this to choose left',
                                       pos=[self.posNavL[0]+0.3, -0.9],
                                       height=self.heightNav,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.navRight = visual.TextStim(win=self.screen,
                                          text='Press this to choose right',
                                          pos=[self.posNavR[0]-0.3, -0.9],
                                          height=self.heightNav,
                                          color=self.color,
                                          wrapWidth=self.wrapWidth)
        self.respLeft = visual.ImageStim(win=self.screen,
                                         image=imagePaths.resp_left,
                                         size=self.sizeNav,
                                         pos=[self.posNavL[0]+0.3, self.posNavL[1]])
        self.respRight = visual.ImageStim(win=self.screen,
                                          image=imagePaths.resp_right,
                                          size=self.sizeNav,
                                          pos=[self.posNavR[0]-0.3, self.posNavL[1]])
        # Re-size navigation images
        self.instructLeft.rescaledSize = rescaleStim(self.instructLeft, self.sizeNav, dispInfo)
        self.instructLeft.setSize(self.instructLeft.rescaledSize)
        self.instructRight.rescaledSize = rescaleStim(self.instructRight, self.sizeNav, dispInfo)
        self.instructRight.setSize(self.instructRight.rescaledSize)
        self.respLeft.rescaledSize = rescaleStim(self.respLeft, self.sizeNav, dispInfo)
        self.respLeft.setSize(self.respLeft.rescaledSize)
        self.respRight.rescaledSize = rescaleStim(self.respRight, self.sizeNav, dispInfo)
        self.respRight.setSize(self.respRight.rescaledSize)


    def instruct_1(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='These are the two buttons to move forward and backward during the instructions:',
                                       pos=[0,0.75],
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.instructSet = visual.ImageStim(win=self.screen,
                                            image=self.imagePaths.instruct_set,
                                            pos=[0, 0.4])
        self.textBottom = visual.TextStim(win=self.screen,
                                          text='These are the two buttons to choose the left and right options during the task:',
                                          pos=self.posMid,
                                          height=self.height,
                                          color=self.color,
                                          wrapWidth=self.wrapWidth)
        self.respSet = visual.ImageStim(win=self.screen,
                                        image=self.imagePaths.resp_set,
                                        pos=[0, -0.4])
        # Rescale images
        self.instructSet.rescaledSize = rescaleStim(self.instructSet,self.imageSize*1.5, self)
        self.instructSet.setSize(self.instructSet.rescaledSize)
        self.respSet.rescaledSize = rescaleStim(self.respSet, self.imageSize*1.5, self)
        self.respSet.setSize(self.respSet.rescaledSize)
        # Draw objects
        self.textTop.draw()
        self.instructSet.draw()
        self.textBottom.draw()
        self.respSet.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    def instruct_2(self):
        self.textTop = visual.TextStim(self.screen,
                                       text='We will give you $15 of real money to play our game.',
                                       pos=self.posMid,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        # Draw objects
        self.textTop.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    def instruct_3(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='You will be choosing between two different images:',
                                       pos=self.posHigh,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.textBottom = visual.TextStim(win=self.screen,
                                          text='Each trial you can choose one.',
                                          pos=self.posLow,
                                          height=self.height,
                                          color=self.color,
                                          wrapWidth=self.wrapWidth)
        self.leftStim = visual.ImageStim(win=self.screen,
                                         size=self.imageSize,
                                         image=self.leftStim_path,
                                         pos=self.imagePosL)
        self.rightStim = visual.ImageStim(win=self.screen,
                                          size=self.imageSize,
                                          image=self.rightStim_path,
                                          pos=self.imagePosR)
        self.leftStim.rescaledSize = rescaleStim(self.leftStim, self.imageSize, self)
        self.leftStim.setSize(self.leftStim.rescaledSize)
        self.rightStim.rescaledSize = rescaleStim(self.rightStim, self.imageSize, self)
        self.rightStim.setSize(self.rightStim.rescaledSize)
        # Draw objects
        self.textTop.draw()
        self.textBottom.draw()
        self.leftStim.draw()
        self.rightStim.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    def instruct_4(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='The images are identified by their color and pattern.',
                                       pos=self.posHigh,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.textBottom = visual.TextStim(win=self.screen,
                                          text='On each trial, a particular image will appear either on the left or the right of the screen.',
                                          pos=self.posMid,
                                          height=self.height,
                                          color=self.color,
                                          wrapWidth=self.wrapWidth)
        # Draw objects
        self.textTop.draw()
        self.textBottom.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    def instruct_5(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='When you choose a image it will be indicated with a box. After a moment, you will see a monetary outcome.',
                                       pos=self.posHigh,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.leftStim = visual.ImageStim(win=self.screen,
                                         size=self.imageSize,
                                         image=self.leftStim_path,
                                         pos=self.imagePosL)
        self.rightStim = visual.ImageStim(win=self.screen,
                                          size=self.imageSize,
                                          image=self.rightStim_respPath,
                                          pos=self.imagePosR)
        self.leftStim.rescaledSize = rescaleStim(self.leftStim, self.imageSize, self)
        self.leftStim.setSize(self.leftStim.rescaledSize)
        self.rightStim.rescaledSize = rescaleStim(self.rightStim, self.imageSize, self)
        self.rightStim.setSize(self.rightStim.rescaledSize)
        # Draw objects
        self.textTop.draw()
        self.leftStim.draw()
        self.rightStim.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    # interactive page
    def instruct_6(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='Try to select the left image now.',
                                       pos=self.posHigh,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.leftStim = visual.ImageStim(win=self.screen,
                                         size=self.imageSize,
                                         image=self.leftStim_path,
                                         pos=self.imagePosL)
        self.rightStim = visual.ImageStim(win=self.screen,
                                          size=self.imageSize,
                                          image=self.rightStim_path,
                                          pos=self.imagePosR)
        self.leftStim.rescaledSize = rescaleStim(self.leftStim, self.imageSize, self)
        self.leftStim.setSize(self.leftStim.rescaledSize)
        self.rightStim.rescaledSize = rescaleStim(self.rightStim, self.imageSize, self)
        self.rightStim.setSize(self.rightStim.rescaledSize)
        # Draw response keys
        self.respLeft.draw()
        self.respRight.draw()
        self.navLeft.draw()
        self.navRight.draw()
        # Draw objects
        self.textTop.draw()
        self.leftStim.draw()
        self.rightStim.draw()
        # Flip screen
        self.screen.flip()
        return


    def instruct_7(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='You might gain money, shown as quarters that give you 25c each.\nQuarters you gain on a trial are added to your total amount.',
                                       pos=[0,0.75],
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.textBottom = visual.TextStim(win=self.screen,
                                       text='In this example you would gain 50c, since two quarters are revealed.',
                                       pos=self.posLow,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.outStim = visual.ImageStim(win=self.screen,
                                        image=self.gain_path,
                                        size=self.imageSize,
                                        pos=self.posMid)
        self.outStim.rescaledSize = rescaleStim(self.outStim, self.imageSize, self)
        self.outStim.setSize(self.outStim.rescaledSize)
        # Draw objects
        self.textTop.draw()
        self.textBottom.draw()
        self.outStim.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    def instruct_8(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='Or you might lose money, shown as quarters that take away 25c each.\nQuarters you lose on a trial are removed from your total amount.',
                                       pos=[0,0.75],
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.textBottom = visual.TextStim(win=self.screen,
                                       text='In this example you would lose 50c, since two quarters are revealed.',
                                       pos=self.posLow,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.outStim = visual.ImageStim(win=self.screen,
                                        image=self.loss_path,
                                        size=self.imageSize,
                                        pos=self.posMid)
        self.outStim.rescaledSize = rescaleStim(self.outStim, self.imageSize, self)
        self.outStim.setSize(self.outStim.rescaledSize)
        # Draw objects
        self.textTop.draw()
        self.textBottom.draw()
        self.outStim.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    # conditional page
    def instruct_9_rl(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='The two images might pay out different amounts of reward over the course of the game.',
                                       pos=self.posMid,
                                       height=self.height*1.2,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        # Draw objects
        self.textTop.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    def instruct_9_hm(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='At a given moment, only one of the two images will be correct. This means that it will pay out more.',
                                       pos=self.posHigh,
                                       height=self.height*1.2,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)

        self.textMid = visual.TextStim(win=self.screen,
                                       text='The other image will be incorrect and it will pay out less.',
                                       pos=self.posMid,
                                       height=self.height*1.2,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.textBottom = visual.TextStim(win=self.screen,
                                      text='Which image is correct and which is incorrect might change throughout the game.',
                                      pos=self.posLow,
                                      height=self.height*1.2,
                                      color=self.color,
                                      wrapWidth=self.wrapWidth)

        # Draw objects
        self.textTop.draw()
        self.textMid.draw()
        self.textBottom.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    def instruct_10(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='Note that the position of the images on the screen (whether on the left or the right) has no influence on whether you win or lose.',
                                       pos=self.posMid,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        # Draw objects
        self.textTop.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    def instruct_11(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='We add up the gains and losses you experience and use that to adjust your real bonus money.',
                                       pos=self.posHigh,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)


        self.textBottom = visual.TextStim(win=self.screen,
                                       text='Try to get as much money as possible!',
                                       pos=self.posMid,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        # Draw objects
        self.textTop.draw()
        self.textBottom.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return

    def instruct_12(self):
        self.textTop = visual.TextStim(win=self.screen,
                                       text='Ok, the instructions are over.',
                                       pos=self.posHigh,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)

        self.textMid = visual.TextStim(win=self.screen,
                                       text="Let's do some practice.",
                                       pos=self.posMid,
                                       height=self.height,
                                       color=self.color,
                                       wrapWidth=self.wrapWidth)
        self.textBottom = visual.TextStim(win=self.screen,
                                      text='Please wait a moment for the experimenter.',
                                      pos=self.posLow,
                                      height=self.height,
                                      color=self.color,
                                      wrapWidth=self.wrapWidth)

        # Draw objects
        self.textTop.draw()
        self.textMid.draw()
        self.textBottom.draw()
        # Draw instruction navigation
        self.instructLeft.draw()
        self.instructRight.draw()
        self.navBack.draw()
        self.navForward.draw()
        # Flip screen
        self.screen.flip()
        return
