import React, { useEffect, useRef } from 'react';

const MatrixEffect = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const fontSize = 16;
    const columns = Math.floor(canvas.width / fontSize);
    
    // Define text characters for the matrix rain
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*()';
    
    // Array to store y positions of each column
    const drops = Array(columns).fill(1);

    // Function to draw the matrix rain
    function draw() {
      // Black with slight transparency to create trail effect
      context.fillStyle = 'rgba(0, 0, 0, 0.05)';
      context.fillRect(0, 0, canvas.width, canvas.height);
      
      // Green text color
      context.fillStyle = '#0f0';
      context.font = `${fontSize}px monospace`;
      
      // Loop through each column
      for (let i = 0; i < drops.length; i++) {
        // Pick a random character
        const char = chars[Math.floor(Math.random() * chars.length)];
        
        // Draw the character
        context.fillText(char, i * fontSize, drops[i] * fontSize);
        
        // Reset when the character reaches the bottom of the screen
        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
          drops[i] = 0;
        }
        
        // Move the character down
        drops[i]++;
      }
    }

    // Run the animation
    const interval = setInterval(draw, 35);

    // Handle window resize
    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    // Clean up
    return () => {
      clearInterval(interval);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas 
      ref={canvasRef} 
      style={{ 
        position: 'absolute', 
        top: 0, 
        left: 0, 
        width: '100%', 
        height: '100%', 
        zIndex: 0,
        opacity: 0.15
      }}
    />
  );
};

export default MatrixEffect;