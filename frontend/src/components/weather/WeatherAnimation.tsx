/**
 * Weather Animation Component
 * Displays animated weather effects based on current conditions
 */

import React from 'react';
import { Box, keyframes } from '@mui/material';

interface WeatherAnimationProps {
  weather: string;
}

const rainDrop = keyframes`
  0% {
    top: -10%;
    opacity: 1;
  }
  100% {
    top: 100%;
    opacity: 0.3;
  }
`;

const snowFall = keyframes`
  0% {
    top: -10%;
    opacity: 1;
  }
  100% {
    top: 100%;
    opacity: 0.3;
  }
`;

const cloudFloat = keyframes`
  0% {
    transform: translateX(-20px);
  }
  50% {
    transform: translateX(20px);
  }
  100% {
    transform: translateX(-20px);
  }
`;

const sunRays = keyframes`
  0% {
    transform: rotate(0deg);
    opacity: 0.8;
  }
  50% {
    opacity: 1;
  }
  100% {
    transform: rotate(360deg);
    opacity: 0.8;
  }
`;

const WeatherAnimation: React.FC<WeatherAnimationProps> = ({ weather }) => {
  const renderAnimation = () => {
    const weatherLower = weather.toLowerCase();

    // Rain animation
    if (weatherLower.includes('rain') || weatherLower.includes('drizzle')) {
      return (
        <>
          {[...Array(20)].map((_, i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                left: `${(i * 5) % 100}%`,
                width: '2px',
                height: '20px',
                background: 'linear-gradient(to bottom, rgba(174,194,224,0.8), rgba(174,194,224,0.3))',
                borderRadius: '2px',
                animation: `${rainDrop} ${1 + Math.random() * 0.5}s linear infinite`,
                animationDelay: `${Math.random() * 2}s`,
              }}
            />
          ))}
        </>
      );
    }

    // Snow animation
    if (weatherLower.includes('snow')) {
      return (
        <>
          {[...Array(15)].map((_, i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                left: `${(i * 7) % 100}%`,
                width: '8px',
                height: '8px',
                background: 'white',
                borderRadius: '50%',
                opacity: 0.8,
                animation: `${snowFall} ${3 + Math.random() * 2}s linear infinite`,
                animationDelay: `${Math.random() * 3}s`,
              }}
            />
          ))}
        </>
      );
    }

    // Cloudy animation
    if (weatherLower.includes('cloud') || weatherLower.includes('overcast')) {
      return (
        <>
          {[...Array(5)].map((_, i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                top: `${20 + i * 15}%`,
                left: `${10 + i * 20}%`,
                width: `${60 + Math.random() * 40}px`,
                height: `${30 + Math.random() * 20}px`,
                background: 'rgba(255, 255, 255, 0.15)',
                borderRadius: '50%',
                animation: `${cloudFloat} ${8 + Math.random() * 4}s ease-in-out infinite`,
                animationDelay: `${i * 0.5}s`,
                filter: 'blur(3px)',
              }}
            />
          ))}
        </>
      );
    }

    // Clear/Sunny animation
    if (weatherLower.includes('clear') || weatherLower.includes('sun')) {
      return (
        <Box
          sx={{
            position: 'absolute',
            top: '20%',
            right: '10%',
            width: '100px',
            height: '100px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(255,220,100,0.4) 0%, rgba(255,220,100,0) 70%)',
            animation: `${sunRays} 20s linear infinite`,
            '&::before': {
              content: '""',
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              background: 'radial-gradient(circle, rgba(255,235,150,0.5) 0%, rgba(255,220,100,0.2) 70%)',
            },
          }}
        />
      );
    }

    // Thunderstorm animation
    if (weatherLower.includes('thunder') || weatherLower.includes('storm')) {
      return (
        <>
          {[...Array(15)].map((_, i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                left: `${(i * 7) % 100}%`,
                width: '2px',
                height: '25px',
                background: 'linear-gradient(to bottom, rgba(255,255,255,0.9), rgba(174,194,224,0.4))',
                borderRadius: '2px',
                animation: `${rainDrop} ${0.8 + Math.random() * 0.4}s linear infinite`,
                animationDelay: `${Math.random() * 1.5}s`,
              }}
            />
          ))}
        </>
      );
    }

    // Mist/Fog/Haze animation
    if (weatherLower.includes('mist') || weatherLower.includes('fog') || weatherLower.includes('haze')) {
      return (
        <>
          {[...Array(8)].map((_, i) => (
            <Box
              key={i}
              sx={{
                position: 'absolute',
                top: `${i * 12}%`,
                left: '-10%',
                width: '120%',
                height: '80px',
                background: `linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,${0.1 + Math.random() * 0.15}) 50%, rgba(255,255,255,0) 100%)`,
                animation: `${cloudFloat} ${15 + Math.random() * 5}s ease-in-out infinite`,
                animationDelay: `${i * 0.8}s`,
                filter: 'blur(8px)',
              }}
            />
          ))}
        </>
      );
    }

    return null;
  };

  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        overflow: 'hidden',
        pointerEvents: 'none',
        zIndex: 1,
      }}
    >
      {renderAnimation()}
    </Box>
  );
};

export default WeatherAnimation;
