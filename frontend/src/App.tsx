/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Studio from './pages/Studio';
import KeySetupModal from './components/KeySetupModal';

export default function App() {
  // WHAT: Gate the app behind the key setup modal.
  // WHY: We want every visitor to see the BYOK instructions before hitting /generate.
  //      Once they set a key (or skip), `ready` flips to true and the app loads normally.
  const [ready, setReady] = useState(false);

  return (
    <>
      {/* Show the key setup modal on every fresh session */}
      <KeySetupModal onReady={() => setReady(true)} />

      {/* Only render routes once the user has dismissed the modal */}
      {ready && (
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/studio/:jobId" element={<Studio />} />
          </Routes>
        </BrowserRouter>
      )}
    </>
  );
}

