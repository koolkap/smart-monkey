import './App.css'
import { publicConfig, secretHandlingNotes } from './config'

function App() {
  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">Coding Platform Boilerplate</p>
        <h1>{publicConfig.appName}</h1>
        <p className="lede">
          A Vite + React frontend starter for your coding platform, prepared to connect to an Azure
          Foundry-backed service without exposing secrets in the browser.
        </p>

        <div className="hero-grid">
          <article className="panel accent">
            <span className="label">Frontend</span>
            <strong>Vite + React + TypeScript</strong>
            <p>Fast local development, typed components, and a clean starting point for product UI.</p>
          </article>

          <article className="panel">
            <span className="label">API Target</span>
            <strong>{publicConfig.apiBaseUrl}</strong>
            <p>Point this to your backend or proxy that securely calls Azure Foundry.</p>
          </article>

          <article className="panel">
            <span className="label">Foundry Status</span>
            <strong>{publicConfig.foundryProjectLabel}</strong>
            <p>Region: {publicConfig.foundryRegion}</p>
          </article>
        </div>
      </section>

      <section className="content-grid">
        <article className="card">
          <h2>What is safe in the frontend</h2>
          <ul>
            <li>Application name and non-sensitive labels</li>
            <li>Public backend base URL</li>
            <li>Feature flags intended for client use</li>
          </ul>
        </article>

        <article className="card warning-card">
          <h2>What must stay secret</h2>
          <p>{secretHandlingNotes.warning}</p>
          <ul>
            <li>Azure Foundry API keys</li>
            <li>Service credentials and tokens</li>
            <li>Any secret placed in .env without a backend boundary</li>
          </ul>
        </article>
      </section>
    </main>
  )
}

export default App
