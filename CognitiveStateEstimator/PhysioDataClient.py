#!/usr/bin/env python
# encoding: utf-8

# import standard Python modules
import time
import sys
import os
#import biopacndt module
import biopacndt


def resp_hr_bpm_callback(hardwareIndex, frame, chanInfo):
	print("Hardware Index: %s" %hardwareIndex)
	print("Frame: %s" %frame)
	print("Frame: %s" %chanInfo)


def outputToScreen(index, frame, channelsInSlice):
        """Callback for use with an AcqNdtDataServer to display incoming channel data in the console.
        
        index:  hardware sample index of the frame passed to the callback.
                        to convert to channel samples, divide by the SampleDivider out
                        of the channel structure.
        frame:  a tuple of doubles representing the amplitude of each channel
                        at the hardware sample position in index.  The index of the
                        amplitude in this tuple matches the index of the corresponding
                        AcqNdtChannel structure in channelsInSlice
        channelsInSlice:        a tuple of AcqNdtChannel objects indicating which
                        channels were acquired in this frame of data.  The amplitude
                        of the sample of the channel is at the corresponding location
                        in the frame tuple.
        """
        
        # NOTE:  'index' is set to a hardware acquisition sample index.  In
        # our sample data file, our acquisition sampling rate is 1kHz.
        #
        # Our sample data file uses variable sampling rates, and every
        # channel is downsampled.  The highest channel sampling rate is
        # only 500 Hz.  Therefore, every odd-indexed hardware sample position
        # does not contain any data!
        #
        # If the frame would be empty at a particular hardware index, the
        # callback does get invoked.  As a result, we won't see any odd
        # values of 'index' in our callback.
        
        print("%s | %s" % (index, frame))


def main():
	"""Basic self test code to connect to the first located AcqKnowledge
	server and print out its XML-RPC method list.
	"""
	
	print("---")
	print("Locating AcqKnowledge NDT Servers...")
	serverList = biopacndt.FindAcqNdtServers()
	
	if len(serverList) < 1:
		print("No AcqKnowledge Servers Found")
		return
	
	hostname, port = serverList[0]
	print("Connecting to %s at port %s" % serverList[0])
	acqServer = biopacndt.AcqNdtServer(hostname, port)
	methodList = acqServer.DispatchedMethodList()
	
	print("Dispatched Method List:")
	print("---")
	for	method in methodList:
		print(method)
	print("---")
	
	print("Acq Server [%s:%s]" % (hostname, port))
	print("MP Device Type: %s" % acqServer.getMPUnitType())
	all_channels = acqServer.GetAllChannels()
	print("Initial Channel Labels: %s" %all_channels )
	print("Sampling Rate: %s" % acqServer.getSamplingRate())
	print("Data Connection Method: %s" % acqServer.getDataConnectionMethod())
	print("---")

	
	for channel in all_channels:
	    acqServer.Deliver(channel, True)
	print("Enabled Channel Labels: %s" %acqServer.GetAllChannels() )
	delivery_enabled_channels = acqServer.DeliverAllEnabledChannels()
	singleConnectPort = acqServer.getSingleConnectionModePort()
	print("---")

	# set up an AcqNdtChannelRecorder object to save the data of our
    # first analog channel  on disk.  This will create the binary output
    # file within the "resources" directory.
    #
    # The AcqNdtChannelRecorder takes a full absolute path to the destination
    # file and the AcqNdtChannel object of the channel being recorded.     
	#channelToRecord = delivery_enabled_channels[0]
	#resourcePath = os.getcwd() + os.sep + "resources"
	#filename = "%s-%s.bin" % (channelToRecord.Type, channelToRecord.Index)
	#fullpath = resourcePath + os.sep + filename
	#recorder = biopacndt.AcqNdtChannelRecorder(fullpath,channelToRecord)


	acqDataServer = biopacndt.AcqNdtDataServer(singleConnectPort, delivery_enabled_channels)
	# add our callback functions to the AcqNdtDataServer to process
    # channel data as it is being received.

	#acqDataServer.RegisterCallback("resp_hr_callback", resp_hr_bpm_callback)

    # We will register the "outputtoScreen" function, defined in this file,
    # which will print out the data to the console as it comes in.
	acqDataServer.RegisterCallback("OutputToScreen",outputToScreen)

	# The AcqNdtChannelRecorder has a "Write" callback that we will
    # also register to record the channel data to the file on disk.
	#acqDataServer.RegisterCallback("BinaryRecorder",recorder.Write)

	#Verify Callbacks were properly registered
	print("Data Server Registered Callbacks: %s" %acqDataServer.GetCallbacks())
	print("Data Server Enabled Channels: %s" %acqDataServer.GetEnabledChannels())
	print("---")

	acqDataServer.Start()
	acqServer.WaitForAcquisitionEnd()
	time.sleep(15)
	acqDataServer.Stop()
	
if __name__ == '__main__':
    main()


