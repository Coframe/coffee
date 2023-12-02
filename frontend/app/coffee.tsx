import React, { Suspense } from 'react';

const FallbackComponent = () => <div> ☕ Brewing ... </div>;

const dynamicImport = (componentName) => {
    return React.lazy(() => import(`./brew/${componentName}`)
        .catch(() => {
            return { default: FallbackComponent };
        })
    );
};

const Coffee: React.FC<{ brew: string }> = ({ brew }) => {
    const GeneratedComponent = dynamicImport(brew);

    return (
        <Suspense fallback={FallbackComponent()}>
            <GeneratedComponent />
        </Suspense>
    );
};

export default Coffee;
