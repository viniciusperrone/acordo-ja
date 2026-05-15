import Image from "next/image";

import Header from "../../components/header";
import Footer from "../../components/footer";
import illustration from "../../assets/images/Ilustration.png";
import protectedIcon from "../../assets/icons/protected.svg";
import moneyIcon from "../../assets/money-icon.png";

const floatingIcons = [
  { top: "15%", left: "10%", size: 80 },
  { top: "5%", left: "40%", size: 80 },
  { top: "40%", left: "10%", size: 80 },
  { top: "50%", left: "43%", size: 80 },
  { top: "10%", left: "93.5%", size: 80 },
  { top: "65%", left: "93.5%", size: 80 },
  { top: "80%", left: "70%", size: 80 },
  { top: "80%", left: "35%", size: 80 },
  { top: "85%", left: "2%", size: 80 },
];

export default function Login() {
  return (
    <div className="bg-white min-h-screen flex flex-col">
      <Header />
      <main className="relative flex-1 overflow-hidden flex">
        {floatingIcons.map((icon, index) => (
          <div
            key={index}
            className="pointer-events-none absolute"
            style={{
              top: icon.top,
              left: icon.left,
              width: icon.size,
              height: icon.size,
            }}
          >
            <Image
              src={moneyIcon}
              alt="Floating money icon"
              fill
              sizes="80px"
              className="object-contain"
            />
          </div>
        ))}

        <div className="relative z-20 min-w-full min-h-full flex flex-row items-center justify-between pr-[8%]">
          <div className="pl-[22%]">
            <Image
              src={illustration}
              alt="Illustration"
              className="max-w-full h-auto"
              width={195}
            />
          </div>

          <div className="w-xl py-4 px-6 flex flex-col rounded-3xl bg-[#76B74F]">
              <h3 className="text-2xl font-bold self-center">Fale com a gente</h3>
              <p className="text-center text-[12px]">Preencha o formulário abaixo e entraremos em contato com você</p>

              <div className="grid grid-cols-2 gap-4 pt-5 pb-6">
                <div className="flex flex-col gap-1">
                  <label className="text-inter text-[14px] font-semibold" htmlFor="">Nome</label>
                  <input type="text" className="h-10 border border-[#404040] bg-white text-[#6C757D] rounded-lg px-1.5" placeholder="Digite seu nome"/>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-inter text-[14px] font-semibold" htmlFor="">Email</label>
                  <input type="text" className="h-10 border border-[#404040] bg-white text-[#6C757D] rounded-lg px-1.5" placeholder="Digite seu email"/>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-inter text-[14px] font-semibold" htmlFor="">Telefone / Whatsapp</label>
                  <input type="text" className="h-10 border border-[#404040] bg-white text-[#6C757D] rounded-lg px-1.5" placeholder="(11) 99999-9999"/>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-inter text-[14px] font-semibold" htmlFor="">CPF / CNPJ</label>
                  <input type="text" className="h-10 border border-[#404040] bg-white text-[#6C757D] rounded-lg px-1.5" placeholder="000.000.000-00"/>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-inter text-[14px] font-semibold" htmlFor="">Motivo de contato</label>
                  <input type="text" className="h-10 border border-[#404040] bg-white text-[#6C757D] rounded-lg px-1.5" placeholder="Selecione uma opção"/>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-inter text-[14px] font-semibold" htmlFor="">Detalhes</label>
                  <textarea className="h-20 border border-[#404040] bg-white text-[#6C757D] rounded-lg px-1.5" placeholder="Descreva seu problema ou dúvida..."></textarea>
                </div>
              </div>
              
              <div className="flex flex-col gap-2">
                <button className="h-10 bg-[#1F6C74] font-inter font-bold text-[14px] text-white rounded-lg">Enviar mensagem</button>
                
                <div className="flex flex-row items-center justify-center gap-1.5">
                  <Image 
                    src={protectedIcon}
                    alt="Protected icon"
                    width={20}
                    height={20}
                  />
                  <p className="text-[14px] font-medium self-center">Entraremos em contato com você em breve.</p>
                </div>
              </div>
            </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}