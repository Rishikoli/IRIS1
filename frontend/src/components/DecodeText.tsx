'use client';

import React, { useState, useEffect } from 'react';

interface DecodeTextProps {
    text: string;
    trigger?: boolean;
    className?: string;
    loop?: boolean;
}

const DecodeText: React.FC<DecodeTextProps> = ({ text, trigger = true, className = '', loop = false }) => {
    const [displayText, setDisplayText] = useState(text);
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()';

    useEffect(() => {
        if (!trigger) {
            setDisplayText(text);
            return;
        }

        let interval: NodeJS.Timeout;
        let loopTimeout: NodeJS.Timeout;

        const startAnimation = () => {
            let iteration = 0;
            clearInterval(interval); // Ensure no previous interval is running

            interval = setInterval(() => {
                setDisplayText(
                    text
                        .split('')
                        .map((letter, index) => {
                            if (index < iteration) {
                                return text[index];
                            }
                            return chars[Math.floor(Math.random() * chars.length)];
                        })
                        .join('')
                );

                if (iteration >= text.length) {
                    clearInterval(interval);
                    if (loop) {
                        loopTimeout = setTimeout(startAnimation, 2000); // Loop every 2 seconds
                    }
                }

                iteration += 1 / 3;
            }, 30);
        };

        startAnimation();

        return () => {
            clearInterval(interval);
            clearTimeout(loopTimeout);
        };
    }, [text, trigger, loop]);

    return <span className={className}>{displayText}</span>;
};

export default DecodeText;
