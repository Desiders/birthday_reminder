"""uuid_generate

Revision ID: e8bcee3790d2
Revises: 
Create Date: 2024-02-22 23:01:40.387340

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8bcee3790d2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add uuid_generate_v1, uuid_generate_v3, uuid_generate_v4, uuid_generate_v5 and others
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute(
        """
        create or replace function uuid_generate_v7()
        returns uuid
        as $$
        declare
          unix_ts_ms bytea;
          uuid_bytes bytea;
        begin
          unix_ts_ms = substring(int8send(floor(extract(epoch from clock_timestamp()) * 1000)::bigint) from 3);

          -- use random v4 uuid as starting point (which has the same variant we need)
          uuid_bytes = uuid_send(gen_random_uuid());

          -- overlay timestamp
          uuid_bytes = overlay(uuid_bytes placing unix_ts_ms from 1 for 6);

          -- set version 7
          uuid_bytes = set_byte(uuid_bytes, 6, (b'0111' || get_byte(uuid_bytes, 6)::bit(4))::bit(8)::int);

          return encode(uuid_bytes, 'hex')::uuid;
        end
        $$
        language plpgsql
        volatile;
    """
    )
    op.execute(
        """
        -- Generate a custom UUID v8 with microsecond precision
        create or replace function uuid_generate_v8()
        returns uuid
        as $$
        declare
          unix_ts_ms bytea;
          uuid_bytes bytea;
          timestamp    timestamptz;
          microseconds int;
        begin
          timestamp    = clock_timestamp();
          unix_ts_ms = substring(int8send(floor(extract(epoch from timestamp) * 1000)::bigint) from 3);
          microseconds = (
            cast(extract(microseconds from timestamp)::int
            - (floor(extract(milliseconds from timestamp))::int * 1000
            ) as double precision) * 4.096)::int;

          -- use random v4 uuid as starting point (which has the same variant we need)
          uuid_bytes = uuid_send(gen_random_uuid());

          -- overlay timestamp
          uuid_bytes = overlay(uuid_bytes placing unix_ts_ms from 1 for 6);

          -- set version 8
          uuid_bytes = set_byte(uuid_bytes, 6, (b'1000' || (microseconds >> 8)::bit(4))::bit(8)::int);
          uuid_bytes = set_byte(uuid_bytes, 7, microseconds::bit(8)::int);

          return encode(uuid_bytes, 'hex')::uuid;
        end
        $$
        language plpgsql
        volatile;
    """
    )


def downgrade() -> None:
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
    op.execute("DROP FUNCTION uuid_generate_v7()")
    op.execute("DROP FUNCTION uuid_generate_v8()")
