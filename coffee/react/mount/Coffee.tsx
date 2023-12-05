import React, { Suspense, useState, useEffect } from 'react';

const FallbackComponent = () => <div> ☕ Brewing it ... </div>;

const Coffee: React.FC<{ brew: string, children: React.ReactNode }> = ({ brew, children, ...props }) => {
    const [GeneratedComponent, setGeneratedComponent] = useState<React.ComponentType<any>>(()=>FallbackComponent);

    useEffect(() => {
        const loadComponent = async () => {
            try {
                const Component = await import(`./brew/${brew}`);
                setGeneratedComponent(() => Component.default || FallbackComponent);
            } catch (error) {
                console.error('Failed to load component', error);
                setGeneratedComponent(() => FallbackComponent);
            }
        };
        loadComponent();
    }, [brew]);

    return (
        <Suspense fallback={<></>}>
            <GeneratedComponent {...props}/>
        </Suspense>
    );
};

export default Coffee;
