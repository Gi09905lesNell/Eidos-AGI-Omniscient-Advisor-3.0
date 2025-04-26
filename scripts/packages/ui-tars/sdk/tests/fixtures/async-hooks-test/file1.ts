/*
 * Copyright (c) 2025 Bytedance, Inc. and its affiliates.
 * SPDX-License-Identifier: Apache-2.0
 */
import { GUIAgent } from './guiagent';
import { useConfig } from './context';

export class O1 {
  async fn() {
    const config = useConfig();
    console.log('config', config);
    return config;
  }
}

export class O2 {
  async fn() {
    const config = useConfig();
    console.log('config2', config);
    return config;
  }
}

const o1 = new O1();
const guiAgent = new GUIAgent({
  config: {
    bar: 'foo',
  },
  o: o1,
});

const guiAgent2 = new GUIAgent({
  config: {
    bar2: 'foo2',
  },
  o: o1,
});

const guiAgent3 = new GUIAgent({
  config: {
    bar3: 'foo3',
  },
  o: new O2(),
});
