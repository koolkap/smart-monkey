type PublicAppConfig = {
  appName: string
  apiBaseUrl: string
  foundryProjectLabel: string
  foundryRegion: string
}

export const publicConfig: PublicAppConfig = {
  appName: import.meta.env.VITE_APP_NAME || 'Smart Monkey',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
  foundryProjectLabel: import.meta.env.VITE_FOUNDRY_PROJECT_LABEL || 'Azure Foundry Connected',
  foundryRegion: import.meta.env.VITE_FOUNDRY_REGION || 'Private',
}

export const secretHandlingNotes = {
  warning:
    'Do not place Azure Foundry API keys or secrets in Vite client variables. Keep them in a backend-only environment or secret store.',
}