import Header from './header';
import Diorama from './workshop';

// Copy preserved from michaelscott.me, captured September 17, 2026.
export default function Home(){return <>
  <a className="skip-link" href="#main">Skip to content</a>

  <Header/>

  <main id="main">
    <section className="hero shell" id="top">
      <div className="storyline" aria-label="Career path">
        <strong>Phoenix, Arizona</strong><i></i>
        Photography<i></i>
        Fabrication<i></i>
        Brand<i></i>
        Live experiences<i></i>
        <strong>AI systems</strong>
      </div>

      <div className="hero-grid">
        <div className="hero-copy reveal">
          <p className="eyebrow">AI lead · creative systems builder</p>
          <h1><span>Michael Scott</span>{' '}<span>Cunningham</span></h1>
          <p className="hero-lede">Turning new technology into useful workflows, memorable experiences, and things people can actually use.</p>
          <p className="hero-copy-secondary">Twenty-plus years across photography, design, production, entrepreneurship, event marketing, and creative operations, now focused on practical AI adoption and building the systems around it.</p>
          <div className="hero-actions">
            <a className="button button-dark" href="#experience">See the work</a>
            <a className="button button-light" href="https://www.linkedin.com/in/michael-scott-cunningham" target="_blank" rel="noreferrer">LinkedIn</a>
            <a className="button button-light" href="/Michael_Scott_Cunningham_Resume.pdf" target="_blank" rel="noreferrer">Résumé</a>
          </div>
        </div>

        <div className="hero-model"><Diorama initialIndex={0} /></div>
      </div>

      <div className="snapshot reveal" aria-label="Career summary">
        <article>
          <p className="label">Now</p>
          <h2>AI Lead</h2>
          <p>Leading AI adoption, team enablement, workflow design, model evaluation, automation experiments, and local-agent pilots at Mi-One Brands.</p>
        </article>
        <article>
          <p className="label">Alongside that</p>
          <h2>Event + Creative Marketing</h2>
          <p>Connecting brand strategy, multimedia production, live events, sales enablement, print, and vendor execution across Mi-Pod, Vaping.com, and related brands.</p>
        </article>
        <article>
          <p className="label">Foundation</p>
          <h2>Builder by default</h2>
          <p>Commercial photographer, designer, fabricator, founder, brand specialist, and hands-on problem solver before AI became the newest tool in the shop.</p>
        </article>
      </div>
    </section>

    <section className="section shell" id="experience">
      <div className="section-head reveal">
        <p className="section-index">01 · Experience</p>
        <h2>A career built by following the work.</h2>
      </div>

      <div className="experience-list">
        <article className="experience-row reveal">
          <h3>Event & Creative Marketing Manager / AI Lead</h3>
          <div className="company">Mi-One Brands</div>
          <time dateTime="2022-10">Oct 2022 to present</time>
          <p className="desc">Leading practical AI adoption while directing multimedia, events, sales-enablement materials, production systems, and cross-functional creative execution.</p>
        </article>
        <article className="experience-row reveal">
          <h3>Brand & Image Specialist</h3>
          <div className="company">Trask Performance</div>
          <time dateTime="2020-02/2022-08">Feb 2020 to Aug 2022</time>
          <p className="desc">Owned photography, video, graphics, social content, and event presence for a performance-motorcycle brand.</p>
        </article>
        <article className="experience-row reveal">
          <h3>Founder / Creative Director</h3>
          <div className="company">HeadKace Motorcycle</div>
          <time dateTime="2013-10/2019-08">Oct 2013 to Aug 2019</time>
          <p className="desc">Built a motorcycle business from the ground up across fabrication, brand, sales, operations, vendors, and customer experience.</p>
        </article>
        <article className="experience-row reveal">
          <h3>Owner / Commercial Photographer</h3>
          <div className="company">Michael Scott Photography</div>
          <time dateTime="2007-08/2013-10">Aug 2007 to Oct 2013</time>
          <p className="desc">Commercial photography and production from preproduction and lighting through capture, retouching, design, and final delivery.</p>
        </article>
      </div>
    </section>

    <div className="practice-wrap" id="creative-systems">
      <section className="practice shell">
        <div className="section-model"><Diorama initialIndex={2} selector={false}/></div>
        <div className="practice-copy reveal">
          <p className="number">02 · Creative systems</p>
          <h2>Make the new thing useful.</h2>
          <p className="lead">The interesting part of AI is not the demo. It is what happens when a real team can use it on Monday morning.</p>
          <p className="body">I translate fast-moving model capabilities into practical workflows, training, governance, creative acceleration, and lightweight tools. The goal is not “more AI.” The goal is better work with less friction.</p>
          <div className="selected">
            <strong>Selected focus</strong>
            <ul>
              <li>AI adoption + training</li>
              <li>Workflow automation</li>
              <li>Local-agent pilots</li>
              <li>Model evaluation</li>
              <li>Vibe-coded tools</li>
            </ul>
          </div>
        </div>
      </section>
    </div>

    <section className="practice reverse shell" id="live-experiences">
      <div className="section-model"><Diorama initialIndex={3} selector={false}/></div>
      <div className="practice-copy reveal">
        <p className="number">03 · Live experiences</p>
        <h2>Make it happen. Then open the doors.</h2>
        <p className="lead"><strong>The idea is the beginning. Getting it into the room is the work.</strong></p>
        <p className="body">I connect the creative side of an event with the practical side: the visuals, vendors, print, staging, logistics, and content capture. There’s always a detail that needs solving before the doors open.</p>
        <div className="selected">
          <strong>Representative work</strong>
          <ul>
            <li>Arizona Bike Week</li>
            <li>Arizona Taco Fest</li>
            <li>Trade-show systems</li>
            <li>Retail environments</li>
            <li>Photo + video production</li>
          </ul>
        </div>
      </div>
    </section>

    <div className="practice-wrap" id="made-to-move">
      <section className="practice shell">
        <div className="section-model"><Diorama initialIndex={5} selector={false}/></div>
        <div className="practice-copy reveal">
          <p className="number">04 · Made to move</p>
          <h2>Always building something.</h2>
          <p className="lead">Motorcycles, BMX, photography, cooking, product ideas, and Arizona roads keep the work connected to motion, materials, and people.</p>
          <p className="body">The mediums change, but the instinct does not: understand how something works, improve it, give it a point of view, then put it into the world.</p>
          <div className="selected">
            <strong>Current experiments</strong>
            <ul>
              <li><a href="https://slyswine.com" target="_blank" rel="noreferrer">Sly Swine Moto Gear</a></li>
              <li>Family recipe box</li>
              <li>Real-time usage tools</li>
              <li>AI-assisted creative systems</li>
            </ul>
          </div>
        </div>
      </section>
    </div>

    <section className="contact shell" id="contact">
      <div className="contact-card reveal">
        <div>
          <p className="label">Reach out</p>
          <h2>Build something that has to work in the real world.</h2>
          <p>AI strategy, creative systems, multimedia, live experiences, product experiments, or the messy problem connecting all of them.</p>
        </div>
        <div className="contact-links">
          <a href="mailto:fugi9963@gmail.com"><span>Email</span></a>
          <a href="/Michael_Scott_Cunningham_Resume.pdf" target="_blank" rel="noreferrer"><span>Résumé</span></a>
          <a href="https://www.linkedin.com/in/michael-scott-cunningham" target="_blank" rel="noreferrer"><span>LinkedIn</span></a>
          <a href="https://github.com/SlySwine" target="_blank" rel="noreferrer"><span>GitHub</span></a>
          <a href="https://x.com/SlySwine" target="_blank" rel="noreferrer"><span>X</span></a>
          <a href="https://www.instagram.com/slyswinemoto/" target="_blank" rel="noreferrer"><span>Instagram</span></a>
        </div>
      </div>
      <footer className="footer">
        <span>© <span>{new Date().getFullYear()}</span> Michael Scott Cunningham</span>
        <span>Phoenix, Arizona</span>
      </footer>
    </section>
  </main>

  </>}
