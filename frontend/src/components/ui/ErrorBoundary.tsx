import { Component, ErrorInfo, ReactNode } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "./Button";

interface Props {
  children?: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error in component:", error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: undefined });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  public render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="flex flex-col items-center justify-center p-8 text-center rounded-lg border border-status-danger/20 bg-status-danger-subtle/30">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-status-danger/10 text-status-danger mb-3">
            <AlertCircle className="h-6 w-6 stroke-[1.5]" />
          </div>
          <h4 className="text-base font-semibold text-text-main">
            Ocorreu uma falha na renderização deste módulo
          </h4>
          <p className="mt-1 text-sm text-text-secondary max-w-sm">
            {this.state.error?.message || "Erro inesperado detectado pelo ErrorBoundary."}
          </p>
          <Button
            variant="danger"
            size="sm"
            onClick={this.handleReset}
            className="mt-4 inline-flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Tentar Novamente
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
