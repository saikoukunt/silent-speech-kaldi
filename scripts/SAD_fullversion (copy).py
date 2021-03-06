# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 16:21:45 2022

@author: lwing
"""

import Boolean
import garbo_SAD
import SAD_struct
import numpy as np
from collections import deque
import threading

class SAD():
    def __init__(self):

        #global boolean for each channel
        self.chan1_active = Boolean.boolean()
        self.chan2_active = Boolean.boolean()
        self.chan3_active = Boolean.boolean()
        self.chan4_active = Boolean.boolean()
        self.chan5_active = Boolean.boolean()
        self.chan6_active = Boolean.boolean()

        self.globalIsFinished = Boolean.boolean()

        #variables for determining speech event
        self.num_active = 0          #number of active channels for a single cycle
        self.num_inactive = 0
        self.active_count = 0        #number of speech events
        self.inactive_count = 0
        self.active_thresh = 1
        self.inactive_thresh = 10
        self.isSpeech = Boolean.boolean()

        #number of samples per packet
        self.num_samples = 240

        #frame_length is in ms
        self.frame_length = 240

    #Each channel has access to the 'packet' struct which contains all 6 channels'
    #raw data as well as an array of booleans for channel activity
    #The global thread will poll over the struct's boolean_table to determine when
    #speech events occur
    #After a string of raw data has been fully processed, the channel thread will
    #wait indefinitely until it gets a new data set to process
    def channel_thread(self, channel, boolean, struct):
        while True:
            channel.setHasData(True)
            active_flag_curr = False
            channel.create_dataFrame()
            x = len(channel.getPrepped())
            for sample_idx in range(x):
                channel.inactivity_check()
                active_flag_curr = channel.isActive()
                
                #1 in the boolean table will represent true
                if active_flag_curr:
                    struct.setBooleanTableEntry(channel.getChannelNum(),sample_idx, 1)
                    boolean.setStatus(True)
                
                #-1 in the boolean table will represent false
                else:
                    struct.setBooleanTableEntry(channel.getChannelNum(),sample_idx, -1)
                    boolean.setStatus(False)
            
            channel.setHasData(False)    
            while not channel.getHasData():
                pass
                #do nothing, waiting for new raw data
            
    def create_SpeechDataQueues(self):
        return [deque(),deque(),deque(),deque(),deque(),deque()]


    def global_thread(self, struct, output):
        while True:
            self.globalIsFinished.setStatus(False)
            speech_data = self.create_SpeechDataQueues()
            bool_len = len(struct.getBooleanTableRow())
            for sample_idx in range(bool_len):
                
                #waiting for each channel to finish its inactivity check on the current downsampled sample
                while (np.count_nonzero(struct.getBooleanTable()[:,sample_idx] == 1) + np.count_nonzero(struct.getBooleanTable()[:,sample_idx] == -1)) < 6 :
                    pass
                    #do nothing
                
                
                self.num_active = np.count_nonzero(struct.getBooleanTable()[[0,1,4,5],sample_idx] == 1)   
                
                if self.isSpeech.getStatus():
                    if self.num_active < 3:
                        self.inactive_count += 1
                    else:
                        self.inactive_count = 0
                
                    if self.inactive_count >= self.inactive_thresh:
                        self.isSpeech.setStatus(False)
                        
                        #6xsomething
                        output_array = np.array([speech_data[0], speech_data[1], speech_data[2], speech_data[3], speech_data[4], speech_data[5]])
                            
                        output.put(output_array)
                        
                        speech_data = self.create_SpeechDataQueues()
                        
                    else:
                        self.isSpeech.setStatus(True)
                        for idx, queue in enumerate(speech_data):
                            for i in range(20):
                                raw_index = int((20 * sample_idx)+i)
                                queue.append(struct.getDataTableEntry(idx, raw_index))
         
            
                else:
                    #updating speech event count
                    if self.num_active >= 3:
                        self.active_count += 1
                    else:
                        self.active_count = 0
            
                    #Speech Event conditional
                    #test
                    if self.active_count >= self.active_thresh:
                        self.isSpeech.setStatus(True)
                        for idx, queue in enumerate(self.speech_data):
                            for i in range(20):
                                raw_index = int((20 * sample_idx)+i)
                                queue.append(struct.getDataTableEntry(idx, raw_index))
                            
                    else:
                        self.isSpeech.setStatus(False)
                        
            self.globalIsFinished.setStatus(True)
            struct.createBooleanTable()             #resetting boolean table
            
            while self.globalIsFinished.getStatus():
                #do nothing until new data is sent
                pass    
    
            

    def run(self, input, output):
        
        #240x6
        data_list = input.get()
        
        
        data_stream1 = data_list[:,0]
        data_stream2 = data_list[:,1]
        data_stream3 = data_list[:,2]
        data_stream4 = data_list[:,3]
        data_stream5 = data_list[:,4]
        data_stream6 = data_list[:,5]
        
        channel1 = garbo_SAD.channel(data_stream1, self.frame_length, 1)
        channel2 = garbo_SAD.channel(data_stream2, self.frame_length, 2)
        channel3 = garbo_SAD.channel(data_stream3, self.frame_length, 3)
        channel4 = garbo_SAD.channel(data_stream4, self.frame_length, 4)
        channel5 = garbo_SAD.channel(data_stream5, self.frame_length, 5)
        channel6 = garbo_SAD.channel(data_stream6, self.frame_length, 6)
        
        data_struct = SAD_struct.sad_struct(np.transpose(data_list),self.num_samples)
        
        t1 = threading.Thread(target=self.channel_thread, args=(channel1, self.chan1_active, data_struct))
        t2 = threading.Thread(target=self.channel_thread, args=(channel2, self.chan2_active, data_struct)) 
        t3 = threading.Thread(target=self.channel_thread, args=(channel3, self.chan3_active, data_struct))
        t4 = threading.Thread(target=self.channel_thread, args=(channel4, self.chan4_active, data_struct)) 
        t5 = threading.Thread(target=self.channel_thread, args=(channel5, self.chan5_active, data_struct))
        t6 = threading.Thread(target=self.channel_thread, args=(channel6, self.chan6_active, data_struct))
        global_thread = threading.Thread(target=self.global_thread, args=(data_struct,output))
        
        
        threads = [t1, t2, t3, t4, t5, t6, global_thread]
        
        #starting threads
        for t in threads:
            t.start()
        
        while True:
            if self.globalIsFinished.getStatus():
                
                #data_list = getDataStream()
                #240x6
                data_list = input.get()
                
                
                data_struct.setDataTable(np.transpose(data_list))
                
                channel1.setRaw(data_list[:,0])
                channel2.setRaw(data_list[:,1])
                channel3.setRaw(data_list[:,2])
                channel4.setRaw(data_list[:,3])
                channel5.setRaw(data_list[:,4])
                channel6.setRaw(data_list[:,5])
                
                channel1.setHasData(True)
                channel2.setHasData(True)
                channel3.setHasData(True)
                channel4.setHasData(True)
                channel5.setHasData(True)
                channel6.setHasData(True)
                
                self.globalIsFinished.setStatus(False)
            
            
            
            
            
            
            
            
            