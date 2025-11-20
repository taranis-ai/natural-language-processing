import os
import pytest
from dotenv import load_dotenv

from natural_language_processing.roberta import Roberta
from natural_language_processing.roberta_german import RobertaGerman
from natural_language_processing.gliner import Gliner


base_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(base_dir, ".env.test")
current_path = os.getcwd()

load_dotenv(dotenv_path=env_file, override=True)


@pytest.fixture(scope="session")
def roberta():
    yield Roberta()


@pytest.fixture(scope="session")
def roberta_german():
    yield RobertaGerman()


@pytest.fixture(scope="session")
def gliner():
    yield Gliner()


@pytest.fixture(scope="session")
def example_text():
    yield "This is an example for NER, about the ACME Corporation which is producing Dynamite in Acme City, which is in Australia and run by Mr. Wile E. Coyote"


@pytest.fixture(scope="session")
def example_text_de():
    yield "Dies ist ein Beispiel für NER, über die ACME Corporation, die Dynamit produziert. Das Unternahmen ist in Acme City, Australien ansässig und wird geführt von Mr. Wile E. Coyote"


@pytest.fixture(scope="session")
def example_cybersec_text():
    yield "Upon opening Emotet maldocs, victims are greeted with fake Microsoft 365 prompt that states 'THIS DOCUMENT IS PROTECTED,' and instructs victims on how to enable macros."


@pytest.fixture(scope="session")
def content1():
    text = (
        "Breaking News: In an unprecedented development that has captured the attention of global markets, the world of technology "
        "and renewable energy is undergoing a transformative shift. In a press conference held at the illustrious headquarters of NovaTech, "
        "an emerging leader in sustainable technology, top executives revealed an ambitious multi-billion dollar plan aimed at revolutionizing "
        "the landscape of renewable energy solutions. The initiative, which is set to reshape the industry, focuses on leveraging cutting-edge "
        "research and innovative breakthroughs to address the challenges posed by climate change and dwindling fossil fuel reserves.\n\n"
        "At the core of this strategic move lies a robust commitment to both innovation and sustainability. NovaTech's new blueprint emphasizes "
        "the integration of state-of-the-art technologies, including advanced solar panels, wind turbines, and energy storage systems, to create "
        "a cohesive framework that not only meets current energy demands but also anticipates future requirements. This bold venture is expected to "
        "accelerate the transition towards cleaner energy sources while setting a new benchmark for corporate responsibility and environmental stewardship.\n\n"
        "Industry analysts are optimistic about the potential ripple effects of NovaTech's announcement. Financial markets responded positively to the "
        "news, with stock prices surging as investors saw the promise of long-term growth and stability. The company has already secured a number of key "
        "partnerships with international stakeholders, signaling a strong endorsement of its vision on a global scale. With strategic collaborations in place, "
        "NovaTech is poised to become a central player in the emerging green economy.\n\n"
        "The initiative also underscores the importance of technological innovation in driving economic and social progress. By channeling significant resources "
        "into research and development, NovaTech aims to foster a culture of creativity and forward-thinking that could inspire similar initiatives across the industry. "
        "The project's success is expected to create new job opportunities, stimulate local economies, and reinforce the country's position as a hub for technological advancement.\n\n"
        "Moreover, NovaTech has unveiled plans to invest in next-generation artificial intelligence algorithms to optimize energy distribution and consumption patterns. "
        "This move is expected to reduce wastage and improve efficiency across various sectors. The company's research division, renowned for its groundbreaking work in "
        "machine learning and data analytics, is collaborating with leading academic institutions and government agencies. This collaboration aims to develop predictive models "
        "that can forecast energy demand with unprecedented accuracy, enabling better management of resources and infrastructure. As these innovative solutions are gradually "
        "integrated into the existing energy grid, NovaTech anticipates a significant reduction in operational costs and an increase in overall performance.\n\n"
        "While the global race towards sustainable energy intensifies, NovaTech's comprehensive strategy is receiving accolades from environmental groups and policymakers alike. "
        "The initiative not only promises economic growth but also aims to mitigate the adverse effects of climate change by lowering carbon emissions and promoting a cleaner, "
        "healthier environment. As the world looks to a future defined by rapid technological advancements and ecological mindfulness, the blend of innovation, sustainability, "
        "and strategic global partnerships is emerging as the cornerstone of progress.\n\n"
        "In addition to its core energy projects, NovaTech has committed to a series of community outreach programs designed to educate the public on renewable energy benefits "
        "and sustainable practices. The company has announced plans for a global tour featuring interactive exhibits, workshops, and partnerships with local governments to implement "
        "pilot projects in urban and rural settings alike. This educational initiative aims to empower communities with the knowledge and tools required to participate actively in "
        "the transition to a greener future. The program's success is anticipated to create a ripple effect, inspiring other corporations and governments to adopt similar measures, "
        "ultimately leading to widespread societal change."
    )
    expected = {"NovaTech": {"Organization"}}
    return text, expected


@pytest.fixture(scope="session")
def content2():
    text = (
        "In a surprising move, a popular European software conglomerate admits to a long-standing vulnerability in its "
        "core codebase, urging users to apply patches immediately. The company, which has dominated the software market for decades, "
        "stated that the flaw was discovered during routine maintenance and promptly communicated to its cybersecurity teams. "
        "Officials have reassured customers that all necessary steps are being taken to fortify their defenses, including deploying "
        "advanced security protocols and collaborating with international experts. Analysts suggest this revelation may trigger a broader "
        "industry re-evaluation of software security practices."
    )
    expected = {"European": {"MISC", "Location"}}
    return text, expected


# Fixture for the third news article
@pytest.fixture(scope="session")
def content3():
    text = (
        "Sophisticated malware targeting Linux servers has been identified, with potentially devastating consequences for enterprise operations. "
        "Cybersecurity firms are actively developing mitigation strategies to combat this new threat, which exploits vulnerabilities in widely used "
        "Linux server applications. In a detailed press release, a leading cybersecurity firm explained how the malware spreads silently through networked systems, "
        "causing significant disruptions before detection. IT departments worldwide have been alerted, and companies are urged to perform immediate system audits "
        "to ensure no breaches have occurred. Ongoing investigations are underway to trace the origins of the malware and assess its impact on corporate infrastructures."
    )
    expected = {"Linux": {"MISC", "Product"}}
    return text, expected


# Fixture for the fourth news article
@pytest.fixture(scope="session")
def content4():
    text = (
        "In a surprising move, a popular European software conglomerate acknowledges a long-standing vulnerability in its core codebase, urging users to apply patches immediately. "
        "The company's executive leadership revealed that the issue stemmed from legacy code that had been overlooked during previous updates. In-depth technical reports have now "
        "been published, detailing the nature of the vulnerability and outlining comprehensive corrective measures. This development has sparked widespread concern among industry peers, "
        "leading to an increased demand for cybersecurity consultations and software audits. Stakeholders remain cautiously optimistic as the company works to restore trust and "
        "reinforce its commitment to digital security."
    )
    expected = {"European": {"MISC", "Location"}}
    return text, expected


@pytest.fixture(scope="session")
def content5():
    text = (
        "Intel collaborates with Oracle to mitigate CVE-2021-5678 vulnerabilities in cloud infrastructures. During a joint press conference, representatives from both tech giants "
        "outlined a comprehensive strategy to enhance security measures across their platforms. While Intel is focusing on hardware-level defenses, Oracle is implementing advanced "
        "software patches designed to prevent the exploitation of known vulnerabilities. Industry experts have lauded this collaborative effort, noting that it sets a new standard "
        "for public-private partnerships in cybersecurity. Customers are urged to update their systems promptly to benefit from these enhancements, and further updates are expected as the partnership evolves."
    )
    expected = {"Intel": {"Organization"}, "Oracle": {"Organization", "Product"}}
    return text, expected


@pytest.fixture(scope="session")
def content6():
    text = (
        "In a surprising twist in the tech industry, BrightMinds, a rapidly growing startup, has announced a breakthrough in quantum computing technology that promises "
        "to redefine computing as we know it. The company’s innovative approach leverages quantum bits (qubits) in unprecedented ways to solve complex computational problems far "
        "more efficiently than classical computers. Experts predict that this breakthrough could revolutionize industries ranging from cryptography to pharmaceuticals, ushering in a new era "
        "of computational capabilities.\n\n"
        "The research team at BrightMinds has dedicated years to refining their proprietary algorithms and developing advanced error-correction techniques. Their system integrates "
        "high-fidelity qubit control with sophisticated quantum error correction protocols, ensuring that quantum coherence is maintained over longer periods—a challenge that has long "
        "hampered the scalability of quantum systems. This innovative solution addresses one of the most significant obstacles in the field, potentially paving the way for scalable quantum "
        "architectures capable of handling real-world applications. Moreover, the startup is collaborating with several leading academic institutions and research labs worldwide, "
        "fostering an environment of shared knowledge and rapid innovation.\n\n"
        "Industry analysts have hailed the announcement as a watershed moment in the evolution of computing. They emphasize that the new platform not only promises to boost processing speeds, "
        "but also offers groundbreaking advancements in secure communications and data encryption. Several major venture capital firms have already expressed keen interest, positioning BrightMinds "
        "to secure substantial funding for the next phase of development. As quantum technology continues to evolve at an unprecedented pace, this breakthrough is seen as a pivotal step toward "
        "realizing the long-anticipated promise of quantum advantage in both commercial and scientific applications."
    )
    expected = {"BrightMinds": {"Organization"}}
    return text, expected


@pytest.fixture(scope="session")
def content7():
    text = (
        "At the International Trade Summit held in Geneva, world leaders, top economists, and key policymakers from over 50 nations gathered to address the evolving landscape "
        "of global commerce and to strategize solutions for emerging economic challenges. The summit was marked by a series of high-level discussions that delved into topics such as "
        "supply chain resilience, digital transformation, and the integration of sustainable practices within international trade frameworks. Delegates emphasized that in order to "
        "maintain economic stability, nations must adopt innovative approaches that promote flexibility and adaptability in a rapidly changing global market.\n\n"
        "Over the course of the three-day event, the summit provided a platform for negotiating critical bilateral and multilateral trade agreements. Leaders shared insights on reducing "
        "trade barriers, streamlining customs procedures, and leveraging advanced digital technologies, such as blockchain, to enhance the transparency and efficiency of cross-border "
        "transactions. Several keynote speeches highlighted the substantial economic benefits of modernizing trade infrastructure, including increased job creation, improved access to emerging "
        "markets, and the fostering of sustainable economic growth. Policy experts underscored the role of innovation in creating more resilient and competitive trade networks.\n\n"
        "A significant focus of the summit was on the importance of public-private partnerships in driving economic progress. Representatives from major multinational corporations presented "
        "initiatives that involve investments in green technologies and sustainable business practices, aligning commercial objectives with environmental responsibility. These partnerships "
        "were portrayed as essential in addressing the challenges posed by climate change while ensuring long-term economic stability in an era of global interconnectedness. In addition, "
        "policymakers proposed new frameworks for international cooperation that aim to harmonize regulations, reduce bureaucratic obstacles, and foster a more predictable trading environment.\n\n"
        "Beyond the formal negotiations, the summit facilitated numerous side meetings and networking sessions where delegates exchanged innovative ideas and collaborated on strategies to navigate "
        "the complexities of a post-pandemic world economy. Participants agreed that collaborative efforts and strategic foresight are crucial in mitigating economic volatility and unlocking new growth "
        "opportunities. The event concluded with a series of actionable commitments, laying the groundwork for enhanced trade partnerships and setting the stage for a new era of global economic collaboration. "
        "Attendees left the summit with a shared sense of urgency and optimism, prepared to implement the agreed-upon measures and drive meaningful change in the international trading system."
    )
    expected = {"Geneva": {"Location"}}
    return text, expected


@pytest.fixture(params=["content1", "content2", "content3", "content4", "content5", "content6", "content7"])
def article(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="session")
def extended_output_schema():
    yield {
        "$id": "",
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Entity List",
        "description": "A list of named-entity objects",
        "type": "array",
        "items": {
            "type": "object",
            "title": "Named Entity Info",
            "description": "Information about a single recognized entity",
            "properties": {
                "value": {
                    "type": "string",
                },
                "type": {
                    "type": "string",
                },
                "probability": {
                    "type": "number",
                },
                "position": {
                    "type": "string",
                },
            },
            "required": ["value", "type"],
        },
    }


@pytest.fixture
def entities_en():
    entities = [
        {"idx": 1, "text": "Russia", "label": "Location"},
        {"idx": 2, "text": "russian", "label": "Location"},
        {"idx": 3, "text": "Willem Defoe", "label": "Person"},
        {"idx": 4, "text": "Defoe", "label": "Person"},
        {"idx": 5, "text": "prices", "label": "Misc"},
        {"idx": 6, "text": "price", "label": "Misc"},
    ]
    text = (
        "Russia was mentioned in the article, and a russian diplomat was quoted. "
        "The actor Willem Defoe gave a speech, and later only Defoe was mentioned. "
        "The prices have been falling, but the word price is also common in the text."
    )
    return entities, text


@pytest.fixture
def entities_de():
    entities = [
        {"idx": 1, "text": "Spanien", "label": "Location"},
        {"idx": 2, "text": "Spanier", "label": "Location"},
        {"idx": 3, "text": "Russland", "label": "Location"},
        {"idx": 4, "text": "russischen", "label": "Location"},
        {"idx": 5, "text": "Katzen", "label": "Misc"},
        {"idx": 6, "text": "Katze", "label": "Misc"},
        {"idx": 7, "text": "Burroughs", "label": "Person"},
        {"idx": 8, "text": "William S. Burroughs", "label": "Person"},
    ]
    text = (
        "Spanien wurde in dem Bericht erwähnt, ebenso ein Spanier. "
        "Russland ist ein großes Land, und die russischen Beziehungen wurden diskutiert. "
        "Die Katzen spielten im Garten, aber eine einzelne Katze schlief auf dem Sofa. "
        "Der Autor William S. Burroughs schrieb viele Bücher, später wurde nur Burroughs genannt."
    )
    return entities, text
