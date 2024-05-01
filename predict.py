print("RUNING....")
import numpy as np
import glob
import os
import librosa
import keras

print('Loading Model....')
# Load the trained Keras model - create_audio_classification_model.h5
model_filename = 'create_audio_classification_model.h5'
trained_model = keras.models.load_model(model_filename)
print('Model Loaded....')


def get_wav_files_in_folder(folder_path):
    # Construct the search pattern for WAV files
    search_pattern = os.path.join(folder_path, '*.wav')

    # Use glob to get a list of paths matching the pattern
    wav_files = glob.glob(search_pattern)

    return wav_files



def concatenate_audio_files(input_files):
    try:
        combined_signal, combined_sr = librosa.load(input_files[0], sr=None)
        for file_path in input_files[1:]:
            signal, sr = librosa.load(file_path, sr=None)
            combined_signal = np.concatenate([combined_signal, signal])
    except Exception as e:
        print(f"Error encountered while loading audio files: {e}")
        return None, None

    return combined_signal, combined_sr


def extract_audio_features(audio_signal, sr):
    try:
        chroma_stft = librosa.feature.chroma_stft(y=audio_signal, sr=sr)
        rmse = librosa.feature.rms(y=audio_signal)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_signal, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_signal, sr=sr)
        features = np.hstack([chroma_stft.mean(axis=1), rmse.mean(), spectral_centroid.mean(), spectral_bandwidth.mean()])
        return features
    except Exception as e:
        print(f"Error processing audio signal: {str(e)}")
        return None


print('Loading Audio Files....')
file = 'audio_recordings'
paths = get_wav_files_in_folder(file)
# Load the combined audio file and extract features
combined_audio, sr = concatenate_audio_files(paths)

# Check if loading and concatenation were successful
if combined_audio is not None:
    print('Extracting Audio Features....')
    # Extract features from the combined audio
    audio_features = extract_audio_features(combined_audio,sr)

    if audio_features is not None:
        # Reshape the features to match the model's expected input shape
        audio_features_reshaped = audio_features.reshape(1, -1)
        print('Predicting....')

        # Make predictions using the trained model
        prediction = trained_model.predict(audio_features_reshaped)

        if prediction is not None:
            print(f"The predicted label for the audio file is: {prediction}")
            print('\n\n\n\n')
            print(f"""            *****************************************************
            Probabilty of not having respiratory disease {prediction[0][0]*100:.4f}
            Probabilty of having respiratory disease {prediction[0][1]*100:.4f}
            *********************************************************""")
            print('\n\n\n\n')
        else:
            print('Failed')
    else:
        print('Error extracting audio features.')
else:
    print('Error loading or concatenating audio files.')

