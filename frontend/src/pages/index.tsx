import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import VideoGenerator from '@/components/VideoGenerator';
import QueuePanel from '@/components/QueuePanel';
import Header from '@/components/Header';
import { QueueProvider } from '@/utils/queueContext';

export default function Home() {
  return (
    <QueueProvider>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <Head>
          <title>Ovi - AI Video Generation Studio</title>
          <meta name="description" content="Generate stunning videos with AI" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <Header />

        <main className="container mx-auto px-4 py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Main Generator Panel */}
              <div className="lg:col-span-2">
                <VideoGenerator />
              </div>

              {/* Queue Panel */}
              <div className="lg:col-span-1">
                <QueuePanel />
              </div>
            </div>
          </motion.div>
        </main>

        {/* Footer */}
        <footer className="mt-16 py-6 text-center text-gray-400 text-sm">
          <p>Ovi Video Generation Studio - Powered by AI</p>
          <p className="mt-2">© 2025 Character AI. All rights reserved.</p>
        </footer>
      </div>
    </QueueProvider>
  );
}
