import time
import os
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv, find_dotenv
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = "C:/Users/pnl1aa3e/Documents/Git/etos-jda-store-service/service/default.env"
print("******************************")


load_dotenv(DOTENV)


print(DOTENV)

print("******************************")
class Settings(BaseSettings):
    app_name: str = "etos-jda-connector"
    environment: str = "dev"
    disable_json_logs: bool = False
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        extra="ignore",
        env_file_encoding="utf-8"
    )

class JDASettings(BaseSettings):
    jda_database_user: str
    jda_database_password: SecretStr
    jda_database_connection_string_dns: SecretStr
    user: str = "CSG"

    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        extra="ignore",
        env_file_encoding="utf-8"
    )    

class GraphQLSettings(BaseSettings):
    supergraph_spn: str
    supergraph_url: str
    access_token: str | None = None
    access_expires_on: int | None = None
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
        extra="ignore",
        env_file_encoding="utf-8"
    )

    def refresh_token(self):
        """Refresh the access token."""
        credential = DefaultAzureCredential()
        token = credential.get_token(f"{self.supergraph_spn}/.default")
        self.access_token = token.token
        self.access_expires_on = token.expires_on

    @property
    def authorization_header(self) -> dict[str, str]:
        if self.access_token is None or self.access_expires_on is None or self.access_expires_on < time.time() - 60:
            self.refresh_token()
        return {
            "Authorization": f"Bearer {self.access_token}"
        }

settings=Settings()
dba_settings = JDASettings()
graphql_settings = GraphQLSettings()
# Print settings to verify they are loaded correctly
print(settings)
print(dba_settings)
print(graphql_settings)

