import React, { useState, useEffect, useRef } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Trash2, Send } from 'lucide-react-native';
import { useAudioRecorder, RecordingPresets, requestRecordingPermissionsAsync } from 'expo-audio';
import { styles } from './styles';

export default function RecordingBar({ onSend, onCancel }) {
  const [isPaused, setIsPaused] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const recordingTimer = useRef(null);
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);

  useEffect(() => {
    startRecording();
    return () => {
      if (recordingTimer.current) {
        clearInterval(recordingTimer.current);
      }
    };
  }, []);

  async function startRecording() {
    try {
      const { status } = await requestRecordingPermissionsAsync();
      if (status === 'granted') {
        await recorder.prepareToRecordAsync();
        recorder.record();
        setRecordingDuration(0);
        recordingTimer.current = setInterval(() => {
          setRecordingDuration(prev => prev + 1);
        }, 1000);
      } else {
        alert("Microphone permission is required to record audio.");
        onCancel();
      }
    } catch (err) {
      console.error('Failed to start recording', err);
      // Fallback for emulator where hardware might occasionally fail
      setRecordingDuration(0);
      recordingTimer.current = setInterval(() => {
        setRecordingDuration(prev => prev + 1);
      }, 1000);
    }
  }

  async function stopAndSendRecording() {
    if (recordingTimer.current) {
      clearInterval(recordingTimer.current);
      recordingTimer.current = null;
    }
    try {
      await recorder.stop();
      const uri = recorder.uri;
      if (uri) {
        onSend(uri);
      } else {
        onCancel();
      }
    } catch (err) {
      console.error('Failed to stop recording', err);
      onCancel();
    }
  }

  async function cancelRecording() {
    if (recordingTimer.current) {
      clearInterval(recordingTimer.current);
      recordingTimer.current = null;
    }
    try {
      await recorder.stop();
    } catch (err) {
      console.error('Failed to cancel recording', err);
    }
    onCancel();
  }

  async function togglePause() {
    try {
      if (isPaused) {
        recorder.record();
        setIsPaused(false);
        recordingTimer.current = setInterval(() => {
          setRecordingDuration(prev => prev + 1);
        }, 1000);
      } else {
        await recorder.pause();
        setIsPaused(true);
        if (recordingTimer.current) {
          clearInterval(recordingTimer.current);
          recordingTimer.current = null;
        }
      }
    } catch (err) {
      console.error('Failed to toggle pause', err);
    }
  }

  const formatRecordingTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <>
      {/* Left Red Trash Button */}
      <TouchableOpacity style={styles.trashCircleButton} onPress={cancelRecording}>
        <Trash2 size={20} color="#EA0038" />
      </TouchableOpacity>

      {/* Middle Pill */}
      <View style={styles.recordingPill}>
        <View style={[styles.redDot, isPaused && { backgroundColor: '#8696a0' }]} />
        <Text style={styles.recordingTimerText}>
          {formatRecordingTime(recordingDuration)}
        </Text>
        
        {/* Waveform */}
        <View style={styles.waveformContainer}>
          {[1, 2, 3, 2, 4, 3, 1, 3, 4, 2, 3, 1].map((h, i) => (
            <View 
              key={i} 
              style={[
                styles.waveformBar, 
                { height: 8 + h * 3 },
                isPaused && { backgroundColor: '#c0c0c0' }
              ]} 
            />
          ))}
        </View>

        {/* Pause Button */}
        <TouchableOpacity style={styles.pauseIconButton} onPress={togglePause}>
          <Text style={{ color: '#00A884', fontWeight: '700', fontSize: 13 }}>
            {isPaused ? 'RESUME' : 'PAUSE'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Right Green Send Button */}
      <TouchableOpacity style={styles.sendCircleButton} onPress={stopAndSendRecording}>
        <Send size={20} color="#fff" />
      </TouchableOpacity>
    </>
  );
}
