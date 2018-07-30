// Copyright 2018 The Exonum Team
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//   http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//! This module is used to collect structures that is shared into `CommandExtension` from `Command`.

use toml;

use std::{collections::BTreeMap, net::SocketAddr};

use blockchain::config::{ConsensusConfig, ValidatorKeys};
use crypto::{PublicKey, SecretKey};

/// Abstract configuration.
pub type AbstractConfig = BTreeMap<String, toml::Value>;

/// Node public configurations.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NodePublicConfig {
    /// Socket address.
    pub address: SocketAddr,
    /// Public keys of a validator.
    pub validator_keys: ValidatorKeys,
    /// Services configurations.
    #[serde(default)]
    pub services_public_configs: AbstractConfig,
}

/// Services configuration
#[derive(PartialEq, Debug, Clone, Serialize, Deserialize)]
pub struct Services {
    /// Configuration for ConfigurationService
    pub configuration: ConfigurationService,
}

impl Default for Services {
    fn default() -> Self {
        Self {
            configuration: ConfigurationService::default(),
        }
    }
}

/// Configuration for ConfigurationService
#[derive(PartialEq, Debug, Clone, Serialize, Deserialize)]
pub struct ConfigurationService {
    /// Number of votes required to commit the new configuration.
    /// This value should be greater than 2/3 and less or equal to the
    /// validators count.
    pub majority_count: Option<u16>,
}

impl Default for ConfigurationService {
    fn default() -> Self {
        Self {
            majority_count: None,
        }
    }
}

/// `SharedConfig` contain all public information that should be shared in the handshake process.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SharedConfig {
    /// Template for common configuration
    pub common: CommonConfigTemplate,
    /// Public node
    pub node: NodePublicConfig,
}

impl NodePublicConfig {
    /// Returns address.
    pub fn address(&self) -> SocketAddr {
        self.address
    }

    /// Returns services configurations.
    pub fn services_public_configs(&self) -> &AbstractConfig {
        &self.services_public_configs
    }
}

/// Base config.
#[derive(PartialEq, Clone, Debug, Serialize, Deserialize, Default)]
pub struct CommonConfigTemplate {
    /// Consensus configuration.
    pub consensus_config: ConsensusConfig,
    /// Services configuration.
    #[serde(default)]
    pub services_config: Services,
    /// General configuration.
    pub general_config: AbstractConfig,
}

/// `NodePrivateConfig` collects all public and secret keys.
#[derive(Debug, Serialize, Deserialize)]
pub struct NodePrivateConfig {
    /// Listen address.
    pub listen_address: SocketAddr,
    /// External address.
    pub external_address: SocketAddr,
    /// Consensus public key.
    pub consensus_public_key: PublicKey,
    /// Consensus secret key.
    pub consensus_secret_key: SecretKey,
    /// Service public key.
    pub service_public_key: PublicKey,
    /// Service secret key.
    pub service_secret_key: SecretKey,
    /// Additional service secret config.
    #[serde(default)]
    pub services_secret_configs: AbstractConfig,
}
