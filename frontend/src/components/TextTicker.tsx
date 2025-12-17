'use client';

import React, { useState, useEffect } from 'react';

interface TextTickerProps {
    texts: string[];
    className?: string;
}

const TextTicker: React.FC<TextTickerProps> = ({ texts, className = '' }) => {
    const [displayText, setDisplayText] = useState('');
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isDecoding, setIsDecoding] = useState(true);
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()';

    useEffect(() => {
        let interval: NodeJS.Timeout;
        let decodeInterval: NodeJS.Timeout;
        const currentText = texts[currentIndex];
        let iteration = 0;

        if (isDecoding) {
            decodeInterval = setInterval(() => {
                setDisplayText(
                    currentText
                        .split('')
                        .map((letter, index) => {
                            if (index < iteration) {
                                return currentText[index];
                            }
                            return chars[Math.floor(Math.random() * chars.length)];
                        })
                        .join('')
                );

                if (iteration >= currentText.length) {
                    clearInterval(decodeInterval);
                    setIsDecoding(false);
                }

                iteration += 1 / 3; // Adjust speed of decoding here
            }, 30);
        } else {
            interval = setTimeout(() => {
                setIsDecoding(true);
                setCurrentIndex((prev) => (prev + 1) % texts.length);
            }, 3000); // Wait 3 seconds before switching
        }

        return () => {
            clearInterval(decodeInterval);
            clearTimeout(interval);
        };
    }, [currentIndex, isDecoding, texts]);

    return (
        <div className={`font-mono text-sm tracking-wider ${className}`}>
            <span className="mr-2 text-green-500">➜</span>
            {displayText}
            <span className="animate-pulse">_</span>
        </div>
    );
};

export default TextTicker;
