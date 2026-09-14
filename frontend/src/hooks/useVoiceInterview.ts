'use client';

import { useState, useEffect, useRef, useCallback } from 'react';

// SpeechRecognition type declarations for browser support
interface IWindow extends Window {
  SpeechRecognition?: any;
  webkitSpeechRecognition?: any;
}

export function useVoiceInterview() {
  const [isListening, setIsListening] = useState(false);
  const [isAiSpeaking, setIsAiSpeaking] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState<number>(0);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [speechSupported, setSpeechSupported] = useState(true);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<string>('');
  const [speechRate, setSpeechRate] = useState<number>(1.0);
  const [audioError, setAudioError] = useState<string | null>(null);

  const recognitionRef = useRef<any>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const animFrameRef = useRef<number | null>(null);

  // Initialize available TTS voices
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const updateVoices = () => {
      if ('speechSynthesis' in window) {
        const available = window.speechSynthesis.getVoices();
        setVoices(available);
        if (available.length > 0 && !selectedVoice) {
          // Prefer natural English voices
          const preferred =
            available.find((v) => v.lang.startsWith('en') && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha') || v.name.includes('David') || v.name.includes('Zira'))) ||
            available.find((v) => v.lang.startsWith('en')) ||
            available[0];
          if (preferred) setSelectedVoice(preferred.name);
        }
      }
    };

    updateVoices();
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.onvoiceschanged = updateVoices;
    }

    return () => {
      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [selectedVoice]);

  // Audio Analyser Loop for Real VU Meter / Waveform
  const startAudioMeter = async () => {
    try {
      if (!navigator.mediaDevices?.getUserMedia) return;
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;

      const audioCtx = new AudioCtx();
      audioContextRef.current = audioCtx;
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      analyserRef.current = analyser;

      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const updateVolume = () => {
        if (!analyserRef.current) return;
        analyserRef.current.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          sum += dataArray[i];
        }
        const average = sum / bufferLength;
        // Scale to 0 - 100 with sensitivity boost
        const scaledVol = Math.min(100, Math.round((average / 128) * 100));
        setVolume(scaledVol);
        animFrameRef.current = requestAnimationFrame(updateVolume);
      };

      updateVolume();
    } catch (err: any) {
      console.warn('[Live Voice] Mic hardware stream not accessible or simulated:', err.message);
      // Generate realistic dynamic simulation audio waveform
      const simulateMeter = () => {
        const simVol = Math.floor(Math.random() * 60) + 20;
        setVolume(simVol);
        animFrameRef.current = requestAnimationFrame(simulateMeter);
      };
      simulateMeter();
    }
  };

  const stopAudioMeter = () => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      audioContextRef.current.close().catch(() => {});
      audioContextRef.current = null;
    }
    setVolume(0);
  };

  // Start Speech-to-Text Listening
  const startListening = useCallback((onResultCallback?: (accumulatedText: string) => void) => {
    if (typeof window === 'undefined') return;
    setAudioError(null);

    const win = window as IWindow;
    const SpeechRecognitionAPI = win.SpeechRecognition || win.webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) {
      setSpeechSupported(false);
      setAudioError('Speech recognition is not natively supported in this browser. Please use Google Chrome, Edge, or Safari.');
      setIsListening(true);
      return;
    }

    try {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (_) {}
      }

      const recognition = new SpeechRecognitionAPI();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onstart = () => {
        setIsListening(true);
        startAudioMeter();
      };

      recognition.onresult = (event: any) => {
        let interim = '';
        let final = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const trans = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            final += trans + ' ';
          } else {
            interim += trans;
          }
        }

        if (final) {
          setTranscript((prev) => {
            const next = prev ? `${prev.trim()} ${final.trim()}` : final.trim();
            if (onResultCallback) onResultCallback(next);
            return next;
          });
        }
        setInterimTranscript(interim);
      };

      recognition.onerror = (event: any) => {
        console.warn('[Live Voice] Speech recognition warning:', event.error);
        if (event.error === 'not-allowed') {
          setAudioError('Microphone permission was denied. Please allow microphone access in your browser settings.');
        }
      };

      recognition.onend = () => {
        setIsListening(false);
        stopAudioMeter();
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err: any) {
      console.error('[Live Voice] Could not start speech recognition:', err);
      setAudioError('Failed to initialize microphone recognition.');
      setIsListening(false);
    }
  }, []);

  // Stop Listening
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (_) {}
      recognitionRef.current = null;
    }
    setIsListening(false);
    stopAudioMeter();
    setInterimTranscript('');
  }, []);

  // AI Text-To-Speech
  const speakAiPrompt = useCallback(
    (text: string, onEnd?: () => void) => {
      if (typeof window === 'undefined' || !('speechSynthesis' in window) || isMuted) {
        return;
      }

      window.speechSynthesis.cancel();

      const cleanText = text.replace(/[*_#`]/g, '');
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.rate = speechRate;
      utterance.pitch = 1.0;

      if (selectedVoice) {
        const found = voices.find((v) => v.name === selectedVoice);
        if (found) utterance.voice = found;
      }

      utterance.onstart = () => {
        setIsAiSpeaking(true);
      };

      utterance.onend = () => {
        setIsAiSpeaking(false);
        if (onEnd) onEnd();
      };

      utterance.onerror = (e) => {
        console.warn('[Live Voice] TTS error/interrupted:', e);
        setIsAiSpeaking(false);
      };

      window.speechSynthesis.speak(utterance);
    },
    [isMuted, speechRate, selectedVoice, voices]
  );

  const stopAiSpeech = useCallback(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsAiSpeaking(false);
    }
  }, []);

  // Simulation for instant demo or fallback
  const simulateVoiceInput = useCallback((sampleAnswer: string, onUpdate: (text: string) => void) => {
    setIsListening(true);
    let index = 0;
    const words = sampleAnswer.split(' ');

    const interval = setInterval(() => {
      if (index < words.length) {
        const currentChunk = words.slice(0, index + 1).join(' ');
        setTranscript(currentChunk);
        onUpdate(currentChunk);
        setVolume(Math.floor(Math.random() * 50) + 40);
        index++;
      } else {
        clearInterval(interval);
        setIsListening(false);
        setVolume(0);
      }
    }, 150);
  }, []);

  return {
    isListening,
    isAiSpeaking,
    isMuted,
    setIsMuted,
    volume,
    transcript,
    setTranscript,
    interimTranscript,
    speechSupported,
    voices,
    selectedVoice,
    setSelectedVoice,
    speechRate,
    setSpeechRate,
    audioError,
    startListening,
    stopListening,
    speakAiPrompt,
    stopAiSpeech,
    simulateVoiceInput,
  };
}
