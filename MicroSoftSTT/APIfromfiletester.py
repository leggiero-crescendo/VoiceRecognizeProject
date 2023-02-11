import os
import azure.cognitiveservices.speech as speechsdk
import time

import librosa
import soundfile as sf
import pandas as pd
from pandas import DataFrame

speech_key, service_region = "Youre-Key", "Youre-region"
global_list = []

# STT special keyword
def from_file(file, reconize_text):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_input = speechsdk.AudioConfig(filename=file)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    result = speech_recognizer.recognize_once_async().get()
    print(result.text)
    if result.text in reconize_text:
        check = True
        last = result.text

    elif result.text.lower() in reconize_text:
        check = True
        last = result.text
    else:
        check = False
        last = result.text
    return check, last

#from_file()       
def keyword(weatherfilename, reconize_text, model):
    
    audio_config = speechsdk.audio.AudioConfig(filename=weatherfilename)
    

    model = speechsdk.KeywordRecognitionModel(model)
    
    # The phrase your keyword recognition model triggers on.
    keyword = reconize_text

    # Create a local keyword recognizer with the default microphone device for input.


    def recognized_cb(evt):
        # Only a keyword phrase is recognized. The result cannot be 'NoMatch'
        # and there is no timeout. The recognizer runs until a keyword phrase
        # is detected or recognition is canceled (by stop_recognition_async()
        # or due to the end of an input file or stream).
        result = evt.result
        if result.reason == speechsdk.ResultReason.RecognizedKeyword:
            print("RECOGNIZED KEYWORD: {}".format(result.text))
            print(result.text)
            checker = True


        nonlocal done
        done = True
        return checker

    def canceled_cb(evt):
        result = evt.result
        if result.reason == speechsdk.ResultReason.Canceled:
            print('CANCELED: {}'.format(result.cancellation_details.reason))
        nonlocal done
        done = True
    
    keyword_recognizer = speechsdk.KeywordRecognizer(audio_config=audio_config)
    done = False
    # Connect callbacks to the events fired by the keyword recognizer.
    print("keyword recognizer", keyword_recognizer)
    
    keyword_recognizer.recognized.connect(recognized_cb)
    keyword_recognizer.canceled.connect(canceled_cb)

    # Start keyword recognition.
    result_future = keyword_recognizer.recognize_once_async(model)
    print(result_future)
    print('Say something starting with "{}" followed by whatever you want...'.format(keyword))
    result = result_future.get()
    last_text = result.text
    if result.text =='hi pony':
        result_checking = True
    else:
        result_checking = False
    print("result",result.text)
    keyword_recognizer.stop_recognition_async()
    return result_checking, last_text
    
    
def down_sample(input_wav, origin_sr, resample_sr, weatherfilename_key):
    y, sr = librosa.load(input_wav, sr=origin_sr)
    resample = librosa.resample(y, sr, resample_sr)
    g_sr = 16000
    sf.write(weatherfilename_key, resample, g_sr, format='WAV', endian='LITTLE', subtype='PCM_16') # file write for wav
    
    print("original wav sr: {}, original wav shape: {}, resample wav sr: {}, resmaple shape: {}".format(origin_sr, y.shape, resample_sr, resample.shape))
    return 

if __name__ == "__main__":
    result_filename = "test.csv"
    reconize_text = ["hi", "hello"] # list
    model = "~.table"
    
    list_num = []
    list_text = []
    list_result_check = []
    
    # STT
    filename = os.listdir('./testwav/')
    number = 0
    numberFalse = 0
    for file in filename:
        if '.wav' in file:
            down_sample('./testwav/'+ file, 44100, 16000, './testresult/'+file)
            result_check, text = keyword('./testresult/'+ file, reconize_text, model) #if you want to from_file just input file and text , keyword
            if result_check:
                number +=1
                list_num.append(str(file))
                list_result_check.append(str(result_check))
                list_text.append(text)

                
            else:
                numberFalse +=1
                print("False")
                list_num.append(str(file))
                list_result_check.append(str(result_check))
                list_text.append(text)
                
                
    result_dict = {"file name": list_num, "Reconize result" : list_result_check, "Reconize text" : list_text}
    df = pd.DataFrame(data = result_dict)
    df.to_csv(result_filename, mode='w')
            
            
    print("True",number, "False", numberFalse, list_num, list_text)
    print(global_list)

