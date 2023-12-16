"use client";

import React, { Suspense, useState, useEffect } from 'react';

const Coffee = ({ brew, children, pass_children, ...props }) => {
    const FallbackComponent = () => <div style={{width:"100%", textAlign:"center", fontSize:"32px"}}> ☕ Brewing
                                        <span style={dotStyle}>.</span>
                                        <span style={{...dotStyle, animationDelay: '0.2s'}}>.</span>
                                        <span style={{...dotStyle, animationDelay: '0.4s'}}>.</span>
                                        <style>
                                        {`@keyframes dot {
                                            0%, 20%, 100% {
                                            opacity: 0;
                                            }
                                            50% {
                                            opacity: 1;
                                            }
                                        }`}
                                        </style></div>;
    const dotStyle = {
        animation: 'dot 1s infinite',
      };
    const [GeneratedComponent, setGeneratedComponent] = useState(()=>FallbackComponent);
    const [loaded, setLoaded] = useState(false);
    brew = brew || "./Brew"

    useEffect(() => {
        const loadComponent = async () => {
            if(loaded) return;
            console.log('loading component...')
            try {
                let Component = undefined;
                if(typeof brew === 'function') {
                    Component = brew;
                } else if(typeof brew === 'string') {
                    const module = await import(`${brew}`)
                    Component = module.default;
                }
                if(!Component) return;
                setLoaded(true);
                setGeneratedComponent(() => Component);
            } catch (error) {
                console.error('Failed to load component', error);
                setGeneratedComponent(() => FallbackComponent);
            }
        };
        // try loading component every 1s
        const interval = setInterval(loadComponent, 1*1000);
        return () => clearInterval(interval);
    }, [brew, loaded]);

    return (
        <Suspense fallback={<></>}>
            <GeneratedComponent {...props} children={pass_children}/>
        </Suspense>
    );
};

export default Coffee;
