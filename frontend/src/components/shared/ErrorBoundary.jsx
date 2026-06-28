import { Component } from 'react'

export class ErrorBoundary extends Component {
  state = { hasError: false }
  static getDerivedStateFromError() { return { hasError: true } }
  render() {
    if (this.state.hasError)
      return <div className="p-8 text-center text-red-600">Something went wrong. Please refresh the page.</div>
    return this.props.children
  }
}
