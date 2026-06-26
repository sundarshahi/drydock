import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  emoji: string;
  description: ReactNode;
  to?: string;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'A team, not a code generator',
    emoji: '🛠️',
    description: (
      <>
        19 specialized agents coordinated by one orchestrator — each owns one job and
        hands verified artifacts to the next, instead of a single generalist doing
        impressions of ten specialists.
      </>
    ),
    to: '/docs/agents/overview',
  },
  {
    title: 'Receipts, not vibes',
    emoji: '🧾',
    description: (
      <>
        Every agent writes a JSON proof of what it produced. A gate won&apos;t open until
        the artifacts are verified on disk — no &quot;done&quot; without evidence.
      </>
    ),
    to: '/docs/concepts/guardrails',
  },
  {
    title: 'A gate that checks your work',
    emoji: '✅',
    description: (
      <>
        The production-readiness gate re-derives test counts, coverage, and performance
        from the actual artifacts. A receipt that claims 90% coverage when the report says
        60% is a blocking failure, not a pass.
      </>
    ),
    to: '/docs/concepts/how-it-works',
  },
  {
    title: 'Security by default',
    emoji: '🔒',
    description: (
      <>
        OWASP 2025 / ASVS / API &amp; LLM Top 10 controls written at build time and
        audited in HARDEN — with a VAPT mode and per-product compliance mapping
        (SOC 2 / GDPR / HIPAA / PCI-DSS).
      </>
    ),
    to: '/docs/security-and-compliance',
  },
  {
    title: 'Idea to launch',
    emoji: '🚀',
    description: (
      <>
        Past shipping: a UX Designer up front, and Growth, Sales, and Customer Success at
        the end turn working software into a launched product.
      </>
    ),
    to: '/docs/agents/go-to-market',
  },
  {
    title: 'Not all-or-nothing',
    emoji: '🎛️',
    description: (
      <>
        14 modes — full greenfield build, harden an existing codebase, pentest, map
        compliance controls, ship, design, launch, or call any single agent directly.
      </>
    ),
    to: '/docs/concepts/modes',
  },
];

function Feature({title, emoji, description, to}: FeatureItem) {
  const body = (
    <div className={styles.featureCard}>
      <div className={styles.featureEmoji} role="img" aria-label={title}>
        {emoji}
      </div>
      <Heading as="h3" className={styles.featureTitle}>
        {title}
      </Heading>
      <p className={styles.featureDesc}>{description}</p>
    </div>
  );
  return (
    <div className={clsx('col col--4', styles.featureCol)}>
      {to ? (
        <Link to={to} className={styles.featureLink}>
          {body}
        </Link>
      ) : (
        body
      )}
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
