# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 17:23:05 2021

@author: Simon Bilik

This module provides the autoencoder training and evaluation based on the folder dataset structure.

Please select the desired model from the module ModelSaved.py as the model argument

"""

import os
import logging
import argparse
import warnings
import traceback
import matplotlib
import configparser

import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from keras.preprocessing.image import img_to_array, load_img

from ModelSaved import ModelSaved
from ModelTrainAndEval import ModelTrainAndEval
from ModelDataGenerators import ModelDataGenerators
from ModelClassificationEnc import ModelClassificationEnc
from ModelClassificationErrM import ModelClassificationErrM
from ModelClassificationSIFT import ModelClassificationSIFT
from ModelClassificationHardNet1 import ModelClassificationHardNet1
from ModelClassificationHardNet2 import ModelClassificationHardNet2
from ModelClassificationHardNet3 import ModelClassificationHardNet3
from ModelClassificationHardNet4 import ModelClassificationHardNet4


## Parse the arguments
def parse_args():
    parser = argparse.ArgumentParser(description = 'Train and evaluate models defined in the ini files of the init directory')
    
    parser.add_argument('--modelTrain', '-t', default = False, type = bool, help = 'Set True for model training')
    parser.add_argument('--modelEval', '-e', default = False, type = bool, help = 'Set True for model evaluation')
    parser.add_argument('--modelPredict', '-p', default = True, type = bool, help = 'Set True for prediction')
    parser.add_argument('--logClear', '-l', default = False, type = bool, help = 'Set True to delete old log be fore operation')

    args = parser.parse_args()

    return args


## Main function
def main():

    # Supress future warnings
    warnings.simplefilter(action = 'ignore', category = FutureWarning)

    # Ini base path
    iniBasePath = './init'

    args = parse_args()

    # Get the arg values
    modelTrain = args.modelTrain
    modelEval = args.modelEval
    modelPredict = args.modelPredict
    logClear = args.logClear

    # Initialize the config parser and the extension filter
    cfg = configparser.ConfigParser()
    ext = ('.ini')
    
    # Initialize the logging
    if logClear:
        os.remove('./ProgramLog.txt')

    logging.basicConfig(filename='./ProgramLog.txt', level=logging.INFO, format='(%(asctime)s %(levelname)-7s) %(message)s')

    # Loop through all ini files in the init directory
    for filename in os.listdir(iniBasePath):

        # Get only the .ini files
        if filename.endswith(ext):

            # Load the ini file and get the arguments
            cfg.read(os.path.join('init', filename))

            # General
            experimentPath = cfg.get('General', 'modelBasePath', fallback = 'NaN')
            labelInfo = cfg.get('General', 'labelInfo', fallback = 'NaN')
            npzSave = cfg.getboolean('General', 'npzSave', fallback = 'False')
            imageDim = (cfg.getint('General', 'imHeight', fallback = '0'), 
                        cfg.getint('General', 'imWidth', fallback = '0'),
                        cfg.getint('General', 'imChannel', fallback = '0'))
            imIndxList = cfg.get('General', 'imIndxList', fallback = 'NaN')

            # Training
            layerSel = cfg.get('Training', 'layerSel', fallback = 'NaN')
            modelSel = cfg.get('Training', 'modelSel', fallback = 'NaN')
            datasetPath = cfg.get('Training', 'datasetPath', fallback = 'NaN')
            batchSize = cfg.getint('Training', 'batchSize', fallback = '0')
            numEpoch = cfg.getint('Training', 'numEpoch', fallback = '0')

            # Prediction
            predictionDataPath = cfg.get('Prediction', 'predictionDataPath', fallback = '.')
            predictionBatchSize = cfg.getint('Prediction', 'batchSize', fallback = '0')
            
            # Parse the img indeces, layers and model's names lists
            imIndxList = (imIndxList.replace(" ", "")).split(",")
            imIndxList = list(map(int, imIndxList))
            layerSel = (layerSel.replace(" ", "")).split(",")
            modelSel = (modelSel.replace(" ", "")).split(",")
            
            # Separate the ini files in log
            logging.info('------------------------------------------------------------------------------------------------')
            logging.info('                                                                                                ')
            logging.info(labelInfo)
            logging.info('                                                                                                ')
            logging.info('------------------------------------------------------------------------------------------------')
            
            # Create experiment directory
            if not os.path.exists(experimentPath):
                os.makedirs(experimentPath)
            
            # Create the experiment related data generator object
            dataGenerator = ModelDataGenerators(experimentPath, datasetPath, labelInfo, imageDim, batchSize, npzSave)     
            
            # Loop through the selected convolutional layers
            for layer in layerSel:

                # Loop through the selected models
                for model in modelSel:
                    
                    # Set the model path
                    modelPath = os.path.join(experimentPath, layer + '_' + labelInfo, model)

                    # Create the model data directory
                    modelDataPath = os.path.join(modelPath, 'modelData')
                    
                    # Create variable to store model data
                    modelData = {}

                    if not os.path.exists(modelDataPath):
                        os.makedirs(modelDataPath)
                    
                    if modelTrain or modelEval:

                        # Train and evaluate the model
                        try:
                            modelObj = ModelTrainAndEval(modelPath, model, layer, dataGenerator, labelInfo, imageDim, imIndxList, numEpoch, modelTrain, modelEval, npzSave)
                            
                            modelData = modelObj.returnProcessedData()
                        except:
                            logging.error('An error occured during the training or evaluation of ' + modelSel + ' model...')
                            traceback.print_exc()
                        else:
                            logging.info('Model ' + model + ' was trained succesfuly...')
                        
                    # Classify the model results 
                    
                    classify = [
                        #ModelClassificationEnc,
                        ModelClassificationErrM,
                        ModelClassificationSIFT,
                        ModelClassificationHardNet1,
                        ModelClassificationHardNet2,
                        ModelClassificationHardNet3,
                        ModelClassificationHardNet4,
                    ]

                    for c in classify:
                        c(modelDataPath, experimentPath, model, layer, labelInfo, imageDim, modelData)
                    
                    # Close the opened figures to spare memory
                    matplotlib.pyplot.close()

    if modelPredict:
        
        ######### Load the best combination
        aeWeightsPath = "data/Cookie_OCC/ConvM1_Cookie_OCC/BAE2/model.weights.h5"
        modelName = 'BAE2'
        layerName = 'ConvM1'
        featureExtractorName = 'SIFT'
        anomalyAlgorythmName = 'Robust covariance'
        imageSize = (imageDim[0], imageDim[1])

        # construct model
        modelObj = ModelSaved(
            modelName,
            layerName,
            imageDim,
            dataVariance = 0.5, 
            intermediateDim = 64,
            latentDim = 32,
            num_embeddings = 32
        )

        feature_extractor = {
            # 'Enc' : ModelClassificationEnc,
            'ErrM' : ModelClassificationErrM,
            'SIFT' : ModelClassificationSIFT,
            'HardNet1' : ModelClassificationHardNet1,
            'HardNet2' : ModelClassificationHardNet2,
            'HardNet3' : ModelClassificationHardNet3,
            'HardNet4' : ModelClassificationHardNet4,
        }[featureExtractorName]

        # load trained weights
        model = modelObj.model
        model.load_weights(aeWeightsPath)
        
        # run and show results
        ax_cols = 2
        ax_rows = 4
        fig, axs = plt.subplots(ax_rows, ax_cols * 2, figsize=(10, 10))
        plt.ion()
        plt.show()

        # get all files
        allowedSuffixes = [
            '.jpg', '.jpeg',
            '.png', '.bmp', '.gif'
        ]
        fileList = map(Path, os.listdir(predictionDataPath))
        imageFileList = [file for file in fileList if file.suffix.lower() in allowedSuffixes]
        images = []
        for imageFile in imageFileList:
            imagePath = Path(predictionDataPath) / imageFile
            image = load_img(imagePath, target_size=imageSize)
            image_array = img_to_array(image)
            images.append(image_array)

            # load images in batches
            if len(images) >= predictionBatchSize:
                input = np.array(images) / 255
                images.clear()
                output = model.predict(input)
                
                for c in range(ax_cols):
                    for r in range(ax_rows):
                        i = int(c * r / ax_cols / ax_rows * len(input))
                        axs[r, 2 * c].imshow(input[i])
                        axs[r, 2 * c + 1].imshow(output[i])

                        axs[r, 2 * c].axis('off')
                        axs[r, 2 * c + 1].axis('off')

                plt.pause(.1)
                plt.draw()

                # Build prediction data
                prediction_data = {
                    'Predict':
                    {
                        'Org': input,
                        'Dec': output,
                    }
                }

                feature_extractor('', '', '', '', '', imageDim, prediction_data, [anomalyAlgorythmName], False)

    return
        
if __name__ == '__main__':
    main()
