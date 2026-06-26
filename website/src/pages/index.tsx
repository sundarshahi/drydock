import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

const PHASES = ['DEFINE', 'BUILD', 'HARDEN', 'SHIP', 'LAUNCH', 'SUSTAIN'];

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className={styles.heroTitle}>
          {siteConfig.title}
        </Heading>
        <p className={styles.heroSubtitle}>{siteConfig.tagline}</p>
        <p className={styles.heroLead}>
          You describe what you want in plain English. A single orchestrator routes the
          work to <strong>19 specialized agents</strong> — product, architecture, UX,
          backend, frontend, QA, security, DevOps, SRE, compliance, docs, and
          go-to-market — that research, build, test, secure, document, and launch a real
          system. You approve at three gates; the agents do the work in between.
        </p>

        <div className={styles.install}>
          <code>/plugin marketplace add sundarshahi/drydock</code>
          <code>/plugin install drydock@drydock</code>
        </div>

        <div className={styles.buttons}>
          <Link className="button button--primary button--lg" to="/docs/intro">
            Get started
          </Link>
          <Link
            className="button button--secondary button--lg"
            href="https://github.com/sundarshahi/drydock">
            View on GitHub
          </Link>
        </div>

        <div className={styles.pipeline} aria-label="Drydock pipeline">
          {PHASES.map((p, i) => (
            <span key={p} className={styles.phaseWrap}>
              <span className={styles.phase}>{p}</span>
              {i < PHASES.length - 1 && <span className={styles.arrow}>→</span>}
            </span>
          ))}
        </div>
        <p className={styles.gatesNote}>
          ◆ Gate 1 requirements · ◆ Gate 2 architecture · ◆ Gate 3 production-readiness
        </p>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title} — ${siteConfig.tagline}`}
      description="Drydock turns Claude Code into a 19-agent product team that takes an idea to a launched product: architecture, UX, tested code, security, CI/CD, compliance, and go-to-market.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
