# -*- coding: utf-8 -*-
"""
Created on Wed Oct  12 17:23:05 2022

@author: Simon Bilik

This class is used for the classification of the evaluated model

"""

import logging
import traceback

import numpy as np

from ModelClassificationBase import ModelClassificationBase

class ModelClassificationEnc(ModelClassificationBase):

    ## Constructor
    def __init__(
            self,
            modelDataPath,
            experimentPath,
            modelSel,
            layerSel,
            labelInfo,
            imageDim,
            modelData,
            anomaly_algorithm_selection = ["Robust covariance", "One-Class SVM", "Isolation Forest", "Local Outlier Factor"],
            visualize = True
        ):

        # Call the parent
        ModelClassificationBase.__init__(
            self,
            modelDataPath,
            experimentPath,
            modelSel,
            layerSel,
            labelInfo,
            imageDim,
            modelData,
            'Enc',
            anomaly_algorithm_selection,
            visualize
        )
        
        # Get data, metrics and classify the data
        try:
            if self.modelData:
                self.procDataFromDict()
            else:
                self.procDataFromFile()
                
            self.dataClassify()
        except:
            logging.error('An error occured during classification using ' + self.featExtName + ' feature extraction method...')
            traceback.print_exc()
        pass


    ## Compute the classification metrics
    def computeMetrics(self, processedData):

        # Get the data
        encData = processedData.get('Enc')
        labels = processedData.get('Lab')
        
        metrics = []
        
        #Flatten the encoded space
        for data in encData:
            metrics.append(data.flatten())

        # Get metrics np array
        metrics = self.normalize2DData(np.array(metrics))

        return metrics, labels
