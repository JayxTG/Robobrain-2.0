import { CheckCircle, Circle, Loader2, XCircle, Zap } from 'lucide-react';

const PipelineProgress = ({ pipeline, executingStep, completedSteps, failedSteps }) => {
  const getStepStatus = (stepNum) => {
    if (failedSteps.includes(stepNum)) return 'failed';
    if (completedSteps.includes(stepNum)) return 'completed';
    if (executingStep === stepNum) return 'executing';
    return 'pending';
  };

  const getStepIcon = (stepNum) => {
    const status = getStepStatus(stepNum);
    
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'executing':
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Circle className="w-5 h-5 text-gray-300 dark:text-gray-600" />;
    }
  };

  const getStepColor = (stepNum) => {
    const status = getStepStatus(stepNum);
    
    switch (status) {
      case 'completed':
        return 'border-green-500 bg-green-50 dark:bg-green-900/20';
      case 'executing':
        return 'border-blue-500 bg-blue-50 dark:bg-blue-900/20';
      case 'failed':
        return 'border-red-500 bg-red-50 dark:bg-red-900/20';
      default:
        return 'border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50';
    }
  };

  return (
    <div className="space-y-3 mb-4">
      {/* Pipeline Header */}
      <div className="flex items-center gap-2 mb-2">
        <Zap className="w-5 h-5 text-purple-600 dark:text-purple-400" />
        <h3 className="text-sm font-semibold text-purple-900 dark:text-purple-100">
          Complex Instruction Pipeline
        </h3>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          ({completedSteps.length}/{pipeline.length} steps)
        </span>
      </div>

      {/* Pipeline Steps */}
      {pipeline.map((step) => (
        <div
          key={step.step}
          className={`relative p-3 rounded-lg border-2 transition-all ${getStepColor(step.step)}`}
        >
          <div className="flex items-start gap-3">
            {/* Step Icon */}
            <div className="flex-shrink-0 mt-0.5">
              {getStepIcon(step.step)}
            </div>

            {/* Step Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">
                  Step {step.step}
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300 capitalize">
                  {step.task}
                </span>
              </div>
              <p className="text-sm text-gray-900 dark:text-gray-100 font-medium">
                {step.description}
              </p>
              {getStepStatus(step.step) === 'executing' && (
                <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                  Executing: {step.prompt.substring(0, 60)}...
                </p>
              )}
            </div>
          </div>

          {/* Connection Line */}
          {step.step < pipeline.length && (
            <div className="absolute left-7 top-full h-3 w-0.5 bg-gray-300 dark:bg-gray-600" />
          )}
        </div>
      ))}
    </div>
  );
};

export default PipelineProgress;
