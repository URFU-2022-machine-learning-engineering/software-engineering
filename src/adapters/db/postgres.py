from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session, declarative_base, relationship

from src.settings.db_settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

Base = declarative_base()


# TODO: Move table representation classes to separate files
class BasicAudioInfo(Base):
    __tablename__ = "basic_audio_info"

    id = Column(Integer, primary_key=True, unique=True)
    filename = Column(String)
    length = Column(Float)
    size = Column(Integer)
    bitrate = Column(Integer)
    samplerate = Column(Integer)
    id3_tags = relationship("ID3Tags", back_populates="basic_audio_info")
    audio_features = relationship("AudioFeatures", back_populates="basic_audio_info")


class ID3Tags(Base):
    __tablename__ = "id3_tags"

    id = Column(Integer, primary_key=True, unique=True)
    audio_id = Column(Integer, ForeignKey("basic_audio_info.id"))
    artist = Column(String)
    album = Column(String)
    genre = Column(String)
    year = Column(String)
    lyrics = Column(String)
    language = Column(String)
    mood = Column(String)
    instrumentation = Column(String)
    basic_audio_info = relationship("BasicAudioInfo", back_populates="id3_tags")


class AudioFeatures(Base):
    __tablename__ = "audio_features"

    id = Column(Integer, primary_key=True, unique=True)
    audio_id = Column(Integer, ForeignKey("basic_audio_info.id"))
    mfccs = Column(ARRAY(Float))
    chroma = Column(ARRAY(Float))
    spectral_centroid = Column(ARRAY(Float))
    zero_crossing_rate = Column(ARRAY(Float))
    spectral_bandwidth = Column(ARRAY(Float))
    spectral_contrast = Column(ARRAY(Float))
    rmse = Column(ARRAY(Float))
    tempo = Column(Float)
    basic_audio_info = relationship("BasicAudioInfo", back_populates="audio_features")


# TODO: Create a separate class for DB connection
def save_audio_info_to_db(audio_info: dict):
    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )

    engine = create_engine(url=connection_url)

    with Session(engine) as session:
        # Save basic audio information
        basic_info = BasicAudioInfo(
            filename=audio_info["filename"],
            length=audio_info["length"],
            size=audio_info["size"],
            bitrate=audio_info["bitrate"],
            samplerate=audio_info["samplerate"],
        )
        session.add(basic_info)
        session.commit()

        # Save ID3 tags
        id3_tags = ID3Tags(
            audio_id=basic_info.id,
            artist=audio_info["artist"],
            album=audio_info["album"],
            genre=audio_info["genre"],
            year=audio_info["year"],
            lyrics=audio_info["lyrics"],
            language=audio_info["language"],
            mood=audio_info["mood"],
            instrumentation=audio_info["instrumentation"],
        )

        # Save audio features
        audio_features = AudioFeatures(
            audio_id=basic_info.id,
            mfccs=audio_info["mfccs"],
            chroma=audio_info["chroma"],
            spectral_centroid=audio_info["spectral_centroid"],
            zero_crossing_rate=audio_info["zero_crossing_rate"],
            spectral_bandwidth=audio_info["spectral_bandwidth"],
            spectral_contrast=audio_info["spectral_contrast"],
            rmse=audio_info["rmse"],
            tempo=audio_info["tempo"],
        )

        session.add_all([id3_tags, audio_features])
        session.commit()
