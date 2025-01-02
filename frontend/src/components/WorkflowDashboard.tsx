import React from 'react';
import { Card, Title, Text } from '@tremor/react';

interface WorkflowStep {
  type: string;
  status: string;
  timestamp: string;
}

interface WorkflowDashboardProps {
  steps: WorkflowStep[];
  result: string;
}

export default function WorkflowDashboard({
  steps,
  result,
}: WorkflowDashboardProps) {
  return (
    <Card className="max-w-4xl mx-auto mt-4">
      <Title>Workflow Execution</Title>

      {/* Steps Timeline */}
      <div className="mt-4">
        {steps.map((step, index) => (
          <div key={index} className="flex items-center gap-2 mb-2">
            <div
              className={`w-3 h-3 rounded-full ${
                step.status === 'completed' ? 'bg-green-500' : 'bg-blue-500'
              }`}
            />
            <Text>
              {step.type} - {step.status}
            </Text>
            <Text className="text-gray-500">{step.timestamp}</Text>
          </div>
        ))}
      </div>

      {/* Result */}
      <Card className="mt-4">
        <Title>Result</Title>
        <Text>{result}</Text>
      </Card>
    </Card>
  );
}
